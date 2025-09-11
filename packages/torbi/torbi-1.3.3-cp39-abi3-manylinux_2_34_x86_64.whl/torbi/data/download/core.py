import shutil
from pathlib import Path

import torch
import torchutil
import torchaudio
import zipfile
import json

import torbi


###############################################################################
# Download datasets
###############################################################################


@torchutil.notify('download')
def datasets(datasets):
    """Download datasets"""
    # Download and format daps dataset
    if 'daps' in datasets:
        daps()
    if 'vctk' in datasets:
        vctk()


def daps():
    """Download daps dataset"""
    import torchaudio

    # Download tarball
    torchutil.download.targz(
        'https://zenodo.org/record/4783456/files/daps-segmented.tar.gz?download=1',
        torbi.DATA_DIR)

    # Delete previous directory
    shutil.rmtree(torbi.DATA_DIR / 'daps', ignore_errors=True)

    # Rename directory
    data_directory = torbi.DATA_DIR / 'daps'
    shutil.move(
        torbi.DATA_DIR / 'daps-segmented',
        data_directory)

    # Get audio files
    audio_files = sorted(
        [path.resolve() for path in data_directory.rglob('*.wav')])
    text_files = [file.with_suffix('.txt') for file in audio_files]

    # Write audio to cache
    speaker_count = {}
    cache_directory = torbi.CACHE_DIR / 'daps'
    cache_directory.mkdir(exist_ok=True, parents=True)
    with torchutil.paths.chdir(cache_directory):

        # Iterate over files
        for audio_file, text_file in torchutil.iterator(
            zip(audio_files, text_files),
            'Formatting daps',
            total=len(audio_files)
        ):

            # Get speaker ID
            speaker = Path(audio_file.stem.split('_')[0])
            if speaker not in speaker_count:

                # Each entry is (index, count)
                speaker_count[speaker] = [len(speaker_count), 0]

            # Update speaker and get current entry
            speaker_count[speaker][1] += 1
            index, count = speaker_count[speaker]

            # Load audio
            audio, sample_rate = torchaudio.load(audio_file)

            # If audio is too quiet, increase the volume
            maximum = torch.abs(audio).max()
            if maximum < .35:
                audio *= .35 / maximum

            # Save at original sampling rate
            speaker_directory = cache_directory / f'{index:04d}'
            speaker_directory.mkdir(exist_ok=True, parents=True)
            output_file = Path(f'{count:06d}.wav')
            torchaudio.save(
                speaker_directory / output_file,
                audio,
                sample_rate)
            shutil.copyfile(
                text_file,
                (speaker_directory / output_file).with_suffix('.txt'))

def vctk():
    """Download vctk dataset"""
    directory = torbi.DATA_DIR / 'vctk'
    directory.mkdir(exist_ok=True, parents=True)
    torchutil.download.zip(
        'https://datashare.ed.ac.uk/download/DS_10283_3443.zip',
        directory)

    # Unzip
    for file in directory.glob('*.zip'):
        with zipfile.ZipFile(file) as zfile:
            zfile.extractall(directory)

    # File locations
    audio_directory = directory / 'wav48_silence_trimmed'

    # Get source files
    audio_files = sorted(list(audio_directory.rglob('*.flac')))
    text_files = [vctk_audio_file_to_text_file(file) for file in audio_files]

    # If the text file doesn't exist, remove corresponding audio file
    text_files = [file for file in text_files if file.exists()]
    audio_files = [
        file for file in audio_files
        if vctk_audio_file_to_text_file(file).exists()]

    # Write audio to cache
    speaker_count = {}
    correspondence = {}
    output_directory = torbi.CACHE_DIR / 'vctk'
    output_directory.mkdir(exist_ok=True, parents=True)
    with torchutil.paths.chdir(output_directory):

        # Iterate over files
        for audio_file, text_file in torchutil.iterator(
            zip(audio_files, text_files),
            'Formatting vctk',
            total=len(audio_files)
        ):

            # Get speaker ID
            speaker = Path(audio_file.stem.split('_')[0])
            if speaker not in speaker_count:

                # Each entry is (index, count)
                speaker_count[speaker] = [len(speaker_count), 0]

            # Update speaker and get current entry
            speaker_count[speaker][1] += 1
            index, count = speaker_count[speaker]

            # Load audio
            audio, sample_rate = torchaudio.load(audio_file)

            # If audio is too quiet, increase the volume
            maximum = torch.abs(audio).max()
            if maximum < .35:
                audio *= .35 / maximum

            # Save at original sampling rate
            speaker_directory = output_directory / f'{index:04d}'
            speaker_directory.mkdir(exist_ok=True, parents=True)
            output_file = Path(f'{count:06d}.wav')
            torchaudio.save(
                speaker_directory / output_file,
                audio,
                sample_rate)
            shutil.copyfile(
                text_file,
                (speaker_directory / output_file).with_suffix('.txt'))

            # Save at system sample rate
            audio = resample(audio, sample_rate)
            torchaudio.save(
                speaker_directory / f'{output_file.stem}-100.wav',
                audio,
                torbi.SAMPLE_RATE)

            # Save file stem correpondence
            correspondence[f'{index:04d}/{output_file.stem}'] = audio_file.stem
        with open('correspondence.json', 'w') as file:
            json.dump(correspondence, file)


###############################################################################
# Utilities
###############################################################################


def resample(audio, sample_rate):
    """Resample audio to ProMoNet sample rate"""
    # Cache resampling filter
    key = str(sample_rate)
    if not hasattr(resample, key):
        setattr(
            resample,
            key,
            torchaudio.transforms.Resample(sample_rate, torbi.SAMPLE_RATE))

    # Resample
    return getattr(resample, key)(audio)


def vctk_audio_file_to_text_file(audio_file):
    """Convert audio file to corresponding text file"""
    text_directory = torbi.DATA_DIR / 'vctk' / 'txt'
    return (
        text_directory /
        audio_file.parent.name /
        f'{audio_file.stem[:-5]}.txt')


def vctk_text_file_to_audio_file(text_file):
    """Convert audio file to corresponding text file"""
    audio_directory = torbi.DATA_DIR / 'vctk' / 'wav48_silence_trimmed'
    return (
        audio_directory /
        text_file.parent.name /
        f'{text_file.stem}.flac')
