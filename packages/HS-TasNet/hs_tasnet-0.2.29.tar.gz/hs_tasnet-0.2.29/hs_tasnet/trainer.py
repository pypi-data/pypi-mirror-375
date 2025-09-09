from __future__ import annotations
from shutil import rmtree
from functools import partial
from random import random, randrange
from pathlib import Path

import torchaudio

import musdb

import torch
from torch import cat, stack, tensor, from_numpy
import torch.nn.functional as F
from torch.nn import Module
from torch.optim import Adam
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import Dataset, DataLoader, ConcatDataset, random_split
from torch.nn.utils.rnn import pad_sequence

import numpy as np

import matplotlib.pyplot as plt

from accelerate import Accelerator

from hs_tasnet.hs_tasnet import HSTasNet

from ema_pytorch import EMA

from einops import rearrange, repeat, reduce

from musdb import DB as MusDB

# constants

pad_sequence = partial(pad_sequence, batch_first = True)

# functions

def exists(v):
    return v is not None

def divisible_by(num, den):
    return (num % den) == 0

def join(arr, delimiter = ' '):
    return delimiter.join(arr)

def satisfy_prob(prob):
    return random() < prob

def rand_range(shape, min, max, device = None):
    rand = torch.rand(shape, device = device)
    return rand * (max - min) + min

def compose(*fns):

    def inner(x):
        for fn in fns:
            x = fn(x)
        return x

    return inner

def db_to_amplitude(db):
    return 10 ** (db / 20.)

def not_improved_last_n_steps(losses, steps):
    if len(losses) <= steps:
        return False

    last_n_losses = losses[-(steps + 1):]

    return (last_n_losses[1:] > last_n_losses[:-1]).all().item()

# sdr

def calculate_sdr(
    target: Tensor,
    pred: Tensor,
    eps = 1e-8
):
    assert target.shape == pred.shape
    target_energy = torch.mean(target ** 2, dim = -1)
    distortion_energy = F.mse_loss(pred, target, reduction = 'none').mean(dim = -1)
    return 10 * torch.log10(target_energy.clamp(min = eps) / distortion_energy.clamp(min = eps))

# dataset collation

def default_collate_fn(
    data: list[tuple[Tensor, Tensor]]
):
    audios, targets = tuple(zip(*data))

    audios, targets = tuple(pad_sequence(t) for t in (audios, targets))

    audio_lens = tuple(t.shape[-1] for t in audios)

    return audios, targets, tensor(audio_lens, device = audios.device)

# dataset related

# musdb18hq dataset wrapper

class MusDB18HQ(Dataset):
    def __init__(
        self,
        dataset_path: str | Path,
        sep_filenames = ('drums', 'bass', 'vocals', 'other'),
        max_audio_length_seconds = None
    ):
        if isinstance(dataset_path, str):
            dataset_path = Path(dataset_path)

        paths = []
        mixture_paths = dataset_path.glob('**/*/mixture.wav')

        # go through all the found paths to mixture.wav
        # and make sure the separated wav files all exist

        for mixture_path in mixture_paths:
            parent_path = mixture_path.parent

            if not all([(parent_path / f'{sep_filename}.wav').exists() for sep_filename in sep_filenames]):
                continue

            paths.append(parent_path)

        self.paths = paths
        self.sep_filenames = sep_filenames

        # if the max_audio_length_seconds is set, will randomly sample a segment from the audio

        assert not exists(max_audio_length_seconds) or max_audio_length_seconds > 0
        self.max_audio_length_seconds = max_audio_length_seconds

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        path = self.paths[idx]

        mixture_path = path / 'mixture.wav'

        # get mixture as 'audio'

        audio, sample_rate = torchaudio.load(str(mixture_path))

        # get all separated audio with filenames as defined by `sep_filenames`

        target_tensors = []
        for sep_filename in self.sep_filenames:
            sep_path = path / f'{sep_filename}.wav'
            target, _ = torchaudio.load(str(sep_path))
            target_tensors.append(target)

        targets = stack(target_tensors)

        # audio lengths for the uncompressed version is much longer

        audio_length = audio.shape[-1]

        if exists(self.max_audio_length_seconds):
            max_length = self.max_audio_length_seconds * sample_rate

            if audio_length > max_length:

                start_index = randrange(audio_length - max_length)

                audio = audio[..., start_index:(start_index + max_length)]
                targets = targets[..., start_index:(start_index + max_length)]

        # return

        return audio, targets

# wrap the musdb MultiTrack if detected

class MusDBDataset(Dataset):
    def __init__(self, musdb_data: MultiTrack):
        self.musdb_data = musdb_data

    def __len__(self):
        return len(self.musdb_data)

    def __getitem__(self, idx):
        sample = self.musdb_data[idx]

        audio = rearrange(sample.audio, 'n s -> s n')

        targets = rearrange(sample.stems[1:], 't n s -> t s n') # the first one is the entire mixture

        audio = audio.astype(np.float32)

        targets = targets.astype(np.float32)

        return audio, targets

# transforms

class CastTorch(Dataset):
    def __init__(self, dataset: Dataset, device = None):
        self.dataset = dataset
        self.device = device

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        audio, targets = self.dataset[idx]

        if isinstance(audio, np.ndarray):
            audio = from_numpy(audio)

        if isinstance(targets, np.ndarray):
            targets = from_numpy(targets)

        if exists(self.device):
            audio = audio.to(self.device)
            targets = targets.to(self.device)

        return audio, targets

class StereoToMonoDataset(Dataset):
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        audio, targets = self.dataset[idx]

        if audio.ndim == 2:
            audio = reduce(audio, 's n -> n', 'mean')

        if targets.ndim == 3:
            targets = reduce(targets, 't s n -> t n', 'mean')

        return audio, targets

class MaxSamples(Dataset):
    def __init__(self, dataset: Dataset, max_samples):
        self.dataset = dataset
        self.max_samples = max_samples

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        audio, targets = self.dataset[idx]

        audio_length = audio.shape[-1]
        max_length = self.max_samples

        if audio_length <= max_length:
            return audio, targets

        start_index_range = audio_length - max_length
        start_index = randrange(start_index_range)

        audio = audio[..., start_index:(start_index + max_length)]
        targets = targets[..., start_index:(start_index + max_length)]

        return audio, targets

# augmentations

class GainAugmentation(Dataset):
    def __init__(
        self,
        dataset: Dataset,
        *,
        prob = 0.5,
        db_range = (-3., 10.),
        clip = False,
        clip_range = (-1., 1.),
        recon_audio_from_targets = False
    ):
        self.dataset = dataset

        self.prob = prob

        self.db_range = db_range
        self.clip = clip
        self.clip_range = clip_range

        self.recon_audio_from_targets = recon_audio_from_targets

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        audio, targets = self.dataset[idx]

        if not satisfy_prob(self.prob):
            return audio, targets

        db_min, db_max = self.db_range

        rand_db_gain = rand_range((), db_min, db_max)
        rand_scale = db_to_amplitude(rand_db_gain)

        audio = audio * rand_scale
        targets = targets * rand_scale

        if self.clip:
            clip_min, clip_max = self.clip_range
            targets = targets.clamp(min = clip_min, max = clip_max)

            if self.recon_audio_from_targets:
                audio = reduce(targets, 't s n -> s n', 'sum')
            else:
                audio = audio.clamp(min = clip_min, max = clip_max)

        return audio, targets

class ChannelSwapAugmentation(Dataset):
    def __init__(self, dataset: Dataset, *, prob = 0.5):
        self.dataset = dataset
        self.prob = prob

    def __len__(self, len):
        return len(self.dataset)

    def __getitem__(self, idx):
        audio, targets = self.dataset[idx]

        if not satisfy_prob(self.prob):
            return audio, targets

        if audio.ndim == 2:
            audio = audio.flip(dims = (0,))

        if targets.ndim == 3:
            targets = targets.flip(dims = (1,))

        return audio, targets

def augment_remix_fn(
    inp: tuple[Tensor, Tensor, Tensor],
    frac_augment = 0.5
):
    """
    this is the effective augmentation used in the separation field that generates synthetic data by combining different tracks across different sources
    """

    audio, targets, audio_lens = inp

    batch_size, device = audio.shape[0], audio.device
    num_augment = int(frac_augment * batch_size)

    if num_augment == 0:
        return inp

    num_sources = targets.shape[1]

    # get indices

    source_arange = torch.arange(num_sources, device = device)
    batch_randperm = torch.randint(0, batch_size, (num_augment, num_sources), device = device)

    # pick out the new targets and ...

    remixed_targets = targets[batch_randperm, source_arange]

    # compose new source from them. take the minimum of the audio lens

    remixed_audio = reduce(remixed_targets, 'b t ... -> b ...', 'sum')
    remixed_audio_lens = reduce(audio_lens[batch_randperm], 'b t -> b', 'min')

    # concat onto the input

    audio = cat((audio[-num_augment:], remixed_audio))
    targets = cat((targets[-num_augment:], remixed_targets))
    audio_lens = cat((audio_lens[-num_augment:], remixed_audio_lens))

    return audio, targets, audio_lens

# classes

class Trainer(Module):
    def __init__(
        self,
        model: HSTasNet,
        dataset: (
            Dataset |
            list[Dataset | MusDB]
            | MusDB
            | None
        ) = None,
        concat_musdb_dataset = False,
        use_full_musdb_dataset = False,
        full_musdb_dataset_root = './data/musdb',
        eval_dataset: Dataset | MusDB | None = None,
        dataset_max_seconds = None,
        random_split_dataset_for_eval_frac = 0., # if set higher than 0., will split off this fraction of the training dataset for evaluation - eval_dataset must be None
        optim_klass = Adam,
        batch_size = 128,
        grad_accum_every = 1,
        learning_rate = 3e-4,
        max_epochs = 10,
        max_steps = None,
        accelerate_kwargs: dict = dict(),
        optimizer_kwargs: dict = dict(),
        cpu = False,
        use_ema = True,
        ema_decay = 0.995,
        ema_kwargs: dict = dict(),
        checkpoint_every = 1,
        checkpoint_folder = './checkpoints',
        eval_sdr = True,
        eval_results_folder = './eval-results',
        decay_lr_factor = 0.5,
        decay_lr_if_not_improved_steps = 3,    # decay learning rate if validation loss does not improve for this amount of epochs
        early_stop_if_not_improved_steps = 10, # they do early stopping if 10 evals without improved loss
        use_wandb = False,
        experiment_project = 'HS-TasNet',
        experiment_run_name = None,
        experiment_hparams: dict = dict(),
        augment_gain = True,
        augment_channel_swap = True,
        augment_remix = True,
        augment_remix_frac = 0.5,
    ):
        super().__init__()

        # hf accelerate

        self.accelerator = Accelerator(
            cpu = cpu,
            gradient_accumulation_steps = grad_accum_every,
            log_with = 'wandb' if use_wandb else None,
            **accelerate_kwargs
        )

        device = self.accelerator.device

        # have the trainer detect if the model is stereo and handle the data accordingly

        self.model_is_stereo = model.stereo
        self.sample_rate = model.sample_rate

        # epochs

        self.max_epochs = max_epochs

        self.max_steps = max_steps

        # saving

        self.checkpoint_every = checkpoint_every

        self.checkpoint_folder = Path(checkpoint_folder)
        self.checkpoint_folder.mkdir(parents = True, exist_ok = True)

        # optimizer

        optimizer = optim_klass(
            model.parameters(),
            lr = learning_rate,
            **optimizer_kwargs
        )

        # take care of datasets
        # in the paper they use MusDB supplemented with own in-house dataset
        # we will allow for automatic concatenation of MusDB (sample or full), or by itself if no dataset were given

        datasets = []

        if exists(dataset):

            # `dataset` can be a list already to be concatted together
            # or just append to datasets list above

            if isinstance(dataset, list):
                datasets = dataset
            else:
                datasets.append(dataset)

        if concat_musdb_dataset:
            # concat the musdb dataset if need be

            if use_full_musdb_dataset:
                musdb_kwargs = dict(root = full_musdb_dataset_root)
            else:
                musdb_kwargs = dict(download = True)

            musdb_dataset = musdb.DB(**musdb_kwargs)

            datasets.append(musdb_dataset)

        # convert MusDB dataset with wrapper if needed

        datasets = [MusDBDataset(ds) if isinstance(ds, MusDB) else ds for ds in datasets] # wrap with musdb dataset to convert to (<audio>, <target>) pairs of right shape

        if isinstance(eval_dataset, MusDB):
            eval_dataset = MusDBDataset(eval_dataset)

        # concat datasets

        all_dataset = ConcatDataset(datasets)

        assert len(all_dataset) > 0, 'your dataset is empty'

        # maybe split dataset for eval

        need_split_train_dataset = random_split_dataset_for_eval_frac > 0
        assert not (need_split_train_dataset and exists(eval_dataset)), f'`eval_dataset` must not be passed in if `random_split_dataset_for_eval_frac` set greater than 0.'

        if not exists(eval_dataset) and need_split_train_dataset:
            train_size = int((1. - random_split_dataset_for_eval_frac) * len(all_dataset))
            eval_size = len(all_dataset) - train_size
            train_dataset, eval_dataset = random_split(all_dataset, (train_size, eval_size))
        else:
            train_dataset = all_dataset

        # print

        self.print(f'\ntraining on dataset of {len(train_dataset)} samples')

        # torch from this point on

        train_dataset = CastTorch(train_dataset, device = device)

        if exists(eval_dataset):
            eval_dataset = CastTorch(eval_dataset, device = device)

        # handle model is not stereo but data is stereo

        if not self.model_is_stereo:
            train_dataset = StereoToMonoDataset(train_dataset)

            if exists(eval_dataset):
                eval_dataset = StereoToMonoDataset(eval_dataset)

        # augmentations
        # only for training `train_dataset`

        if augment_gain:
            train_dataset = GainAugmentation(train_dataset)

        collate_fn = default_collate_fn

        if augment_remix:
            collate_fn = compose(collate_fn, partial(augment_remix_fn, frac_augment = augment_remix_frac))

        # random sample segments if `dataset_max_seconds` is set

        if exists(dataset_max_seconds):
            max_samples = self.sample_rate * dataset_max_seconds
            train_dataset = MaxSamples(train_dataset, max_samples)

            if exists(eval_dataset):
                eval_dataset = MaxSamples(eval_dataset, max_samples)

        # dataloader

        dataloader = DataLoader(train_dataset, batch_size = batch_size, drop_last = True, shuffle = True, collate_fn = collate_fn)

        eval_dataloader = None

        if exists(eval_dataset):
            eval_dataloader = DataLoader(eval_dataset, batch_size = batch_size, drop_last = False, shuffle = True, collate_fn = default_collate_fn)

        self.eval_dataset = eval_dataset

        # evaluation results

        eval_results_folder = Path(eval_results_folder)
        eval_results_folder.mkdir(parents = True, exist_ok = True)

        self.eval_results_folder = eval_results_folder

        # evaluate sdr

        self.eval_sdr = eval_sdr

        # maybe experiment tracker

        if use_wandb:

            try:
                import wandb
            except ImportError:
                print(f'install `wandb` first for experiment tracking')

            self.accelerator.init_trackers(experiment_project, config = experiment_hparams)

            if exists(experiment_run_name):
                wandb_tracker = self.accelerator.trackers[0]
                wandb_tracker.run.name = experiment_run_name

        self.use_wandb = use_wandb

        # decay lr logic

        scheduler = StepLR(optimizer, 1, gamma = decay_lr_factor)

        self.decay_lr_if_not_improved_steps = decay_lr_if_not_improved_steps

        # setup ema on main process

        self.use_ema = use_ema

        if use_ema:
            self.ema_model = EMA(
                model,
                beta = ema_decay,
                forward_method_names = (
                    'sounddevice_stream',
                    'process_audio_file',
                ),
                **ema_kwargs
            )

        # preparing

        (
            self.model,
            self.optimizer,
            self.scheduler,
            self.dataloader
        ) = self.accelerator.prepare(
            model,
            optimizer,
            scheduler,
            dataloader
        )

        # has eval

        self.needs_eval = exists(eval_dataloader)

        # early stopping

        assert early_stop_if_not_improved_steps >= 2
        self.early_stop_steps = early_stop_if_not_improved_steps

        # prepare eval

        if self.needs_eval:
            self.print(f'\nevaluating on dataset of {len(eval_dataset)} samples')

            self.eval_dataloader = self.accelerator.prepare(eval_dataloader)

        # step

        self.register_buffer('step', tensor(0))

        self.register_buffer('zero', tensor(0.), persistent = False)

    def clear_folders(self):
        rmtree(str(self.checkpoint_folder), ignore_errors = True)
        self.checkpoint_folder.mkdir(parents = True, exist_ok = True)

        rmtree(str(self.eval_results_folder), ignore_errors = True)
        self.eval_results_folder.mkdir(parents = True, exist_ok = True)

    @property
    def device(self):
        return self.accelerator.device

    @property
    def unwrapped_model(self):
        return self.accelerator.unwrap_model(self.model)

    @property
    def is_main(self):
        return self.accelerator.is_main_process

    def wait(self):
        return self.accelerator.wait_for_everyone()

    def print(self, *args):
        return self.accelerator.print(*args)

    def log(self, **data):
        return self.accelerator.log(data, step = self.step.item())

    def forward(self):

        acc = self.accelerator

        self.print(f'\nstarting training for HSTasNet with {self.unwrapped_model.num_parameters} params\n')

        exceeds_max_step = False
        past_eval_losses = [] # for learning rate decay and early stopping detection

        # the function for saving checkpoints

        def save_checkpoints(checkpoint_index):
            self.unwrapped_model.save(self.checkpoint_folder / f'hs-tasnet.ckpt.{checkpoint_index}.pt')

            if self.use_ema:
                self.ema_model.ema_model.save(self.checkpoint_folder /f'hs_tasnet.ema.ckpt.{checkpoint_index}.pt') # save ema

        # go through all epochs

        for epoch in range(1, self.max_epochs + 1):

            self.model.train()

            # training steps

            for audio, targets, audio_lens in self.dataloader:

                with acc.accumulate(self.model):
                    loss = self.model(
                        audio,
                        targets = targets,
                        audio_lens = audio_lens,
                        auto_curtail_length_to_multiple = True
                    )

                    acc.backward(loss)

                    self.print(f'[{epoch}] loss: {loss.item():.3f}')

                    self.log(loss = loss)

                    self.optimizer.step()
                    self.optimizer.zero_grad()

                # max steps

                self.step.add_(1)

                exceeds_max_step = exists(self.max_steps) and self.step.item() >= self.max_steps

                if exceeds_max_step:
                    break

            # update ema

            self.wait()

            if self.use_ema and self.is_main:
                self.ema_model.update()

            # maybe eval

            self.wait()

            if self.needs_eval:

                # evaluation at the end of each epoch

                avg_eval_loss = self.zero

                eval_losses = []
                eval_sdr = []

                for eval_audio, eval_targets, eval_audio_lens in self.eval_dataloader:

                    with torch.no_grad():
                        self.model.eval()

                        eval_loss, pred_targets = self.model(
                            eval_audio,
                            targets = eval_targets,
                            audio_lens = eval_audio_lens,
                            auto_curtail_length_to_multiple = True,
                            return_targets_with_loss = True
                        )

                        # store losses - need it for learning rate decay and early stopping logic

                        eval_losses.append(eval_loss)

                        if not self.eval_sdr:
                            continue

                        # derive SDR, which i'm learning, much like FID, is imperfect measure, but a standard in the field

                        eval_len = pred_targets.shape[-1] # may have been auto curtailed
                        eval_targets = eval_targets[..., :eval_len]

                        # fold channels into batch

                        eval_targets_for_sdr, pred_targets_for_sdr = tuple(rearrange(t, 'b t ... n -> (b ...) t n') for t in (eval_targets, pred_targets))

                        # use simplest sdr (not si)

                        sdrs = calculate_sdr(eval_targets_for_sdr, pred_targets_for_sdr)

                        sdrs = reduce(sdrs, 'b t -> t', 'mean')

                        sdrs_string = join([f'{sdr.item():.3f}' for sdr in sdrs])

                        self.print(f'[{epoch}] avg sdr per source: {sdrs_string}')

                        eval_sdr.append(sdrs.mean())

                avg_eval_loss = stack(eval_losses).mean()
                avg_eval_loss = acc.gather_for_metrics(avg_eval_loss).mean()

                past_eval_losses.append(avg_eval_loss)

                self.print(f'[{epoch}] eval loss: {avg_eval_loss.item():.3f}')

                eval_logs = dict(
                    valid_loss = avg_eval_loss,
                )

                if self.eval_sdr and len(eval_sdr) > 0:

                    avg_eval_sdr = stack(eval_sdr).mean()
                    avg_eval_sdr = acc.gather_for_metrics(avg_eval_sdr).mean()

                    self.print(f'[{epoch}] eval average SDR: {avg_eval_sdr.item():.3f}')

                    eval_logs.update(avg_valid_sdr = avg_eval_sdr)

                if self.is_main:
                    model = self.unwrapped_model

                    # take a random sample from eval dataset and store the audio and spectrogram results

                    rand_index = randrange(len(self.eval_dataset))
                    eval_audio, eval_targets = self.eval_dataset[rand_index]

                    with torch.no_grad():
                        model.eval()

                        batched_eval_audio = rearrange(eval_audio, '... -> 1 ...')
                        batched_separated_audio, _ = model(batched_eval_audio)
                        separated_audio = rearrange(batched_separated_audio, '1 ... -> ...')

                    # make sure folder exists - each evaluation epoch gets a folder for separated audio and spec

                    one_eval_result_folder = self.eval_results_folder / str(epoch)
                    one_eval_result_folder.mkdir(parents = True, exist_ok = True)

                    # save eval files (audio and spectrogram) to folder

                    eval_audio_paths = []
                    eval_spec_img_paths = []

                    model.save_tensor_to_file(one_eval_result_folder / 'audio.mp3', eval_audio, overwrite = True)
                    model.save_spectrogram_figure(one_eval_result_folder / 'spec.png', eval_audio, overwrite = True)

                    eval_audio_paths.append(('eval_audio', str(one_eval_result_folder / 'audio.mp3')))
                    eval_spec_img_paths.append(('eval_spec', str(one_eval_result_folder / 'spec.png')))

                    for index, (pred_target_audio, target_audio) in enumerate(zip(separated_audio, eval_targets)):

                        saved_audio_path = one_eval_result_folder / f'target.separated.{index}.mp3'
                        pred_saved_audio_path = one_eval_result_folder / f'pred.target.separated.{index}.mp3'

                        saved_spectrogram_path = one_eval_result_folder / f'target.separated.spectrogram.{index}.png'
                        pred_saved_spectrogram_path = one_eval_result_folder / f'pred.target.separated.spectrogram.{index}.png'

                        model.save_tensor_to_file(saved_audio_path, target_audio, overwrite = True)
                        model.save_tensor_to_file(pred_saved_audio_path, pred_target_audio, overwrite = True)

                        model.save_spectrogram_figure(saved_spectrogram_path, target_audio, overwrite = True)
                        model.save_spectrogram_figure(pred_saved_spectrogram_path, pred_target_audio, overwrite = True)

                        eval_audio_paths.append((f'target_audio_{index}', str(pred_saved_audio_path)))
                        eval_spec_img_paths.append((f'target_spec_{index}', str(pred_saved_spectrogram_path)))

                    # log audio and spec images to wandb experiment if need be

                    if self.use_wandb:
                        from wandb import Audio, Image

                        for name, eval_audio_path in eval_audio_paths:
                            eval_logs[name] = Audio(eval_audio_path, sample_rate = self.sample_rate)

                        for name, eval_spec_img_path in eval_spec_img_paths:
                            eval_logs[name] = Image(eval_spec_img_path)

                self.log(**eval_logs)

            # maybe save

            self.wait()

            if (
                divisible_by(epoch, self.checkpoint_every) and
                self.is_main
            ):
                checkpoint_index = epoch // self.checkpoint_every

                save_checkpoints(checkpoint_index)

            # determine lr decay and early stopping based on eval

            if self.needs_eval:
                # stack validation losses for all epochs

                last_n_eval_losses = stack(past_eval_losses)

                # decay lr if criteria met

                if not_improved_last_n_steps(last_n_eval_losses, self.decay_lr_if_not_improved_steps):
                    self.print(f'decaying learning rate as validation has not improved for {self.decay_lr_if_not_improved_steps} steps')
                    self.scheduler.step()

                # early stop if criteria met

                if not_improved_last_n_steps(last_n_eval_losses, self.early_stop_steps):
                    self.print(f'early stopping at epoch {epoch} since last three eval losses have not improved: {last_n_eval_losses.tolist()}')
                    break

            if exceeds_max_step:
                break

        # cleanup accelerator

        save_checkpoints(-1) # save one last time with checkpoint index -1

        acc.end_training()

        self.print(f'training complete')
