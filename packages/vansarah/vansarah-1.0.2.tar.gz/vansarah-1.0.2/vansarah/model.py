from .istftnet import Decoder
from .modules import CustomAlbert, ProsodyPredictor, TextEncoder
from dataclasses import dataclass
from loguru import logger
from transformers import AlbertConfig
from typing import Dict, Optional, Union
import json
import torch
import os
import gdown
import zipfile

class KModel(torch.nn.Module):
    DRIVE_FILES = {
        "vansarah-v1_0": {
            "config": "https://drive.google.com/uc?id=1TvY-JXpEkuy7YB59GZxxRVjdq9bopN9Q",  # config.json
            "model": "https://drive.google.com/uc?id=1mny9LUr8yTA3MKrph3SYuRW584zyDAkF",   # model.pth
        }
    }
    
    # Thêm thông tin folder voices (file zip)
    VOICES_ZIP = {
        "url": "https://drive.google.com/uc?id=1oYt4goYslnT1cRr0OTLF8Q9tp_qta-Yi",
        "filename": "voices.zip"
    }

    def __init__(
        self,
        model_name: str = "vansarah-v1_0",
        config: Union[Dict, str, None] = None,
        model: Optional[str] = None,
        disable_complex: bool = False,
        cache_dir: str = "./models",
        voices_dir: str = "./voices"  # Thêm tham số voices directory
    ):
        super().__init__()
        os.makedirs(cache_dir, exist_ok=True)
        self.voices_dir = voices_dir

        # Tải folder voices nếu chưa có - PHẦN MỚI THÊM
        self._download_voices_folder()

        drive_info = self.DRIVE_FILES[model_name]

        # tải config nếu chưa có
        if not isinstance(config, dict):
            if not config:
                config_path = os.path.join(cache_dir, f"{model_name}_config.json")
                if not os.path.exists(config_path):
                    logger.info(f"Downloading config from Google Drive to {config_path}")
                    gdown.download(drive_info["config"], config_path, quiet=False)
                config = config_path

            with open(config, "r", encoding="utf-8") as r:
                config = json.load(r)
                logger.debug(f"Loaded config: {config}")

        self.vocab = config["vocab"]
        self.bert = CustomAlbert(AlbertConfig(vocab_size=config["n_token"], **config["plbert"]))
        self.bert_encoder = torch.nn.Linear(self.bert.config.hidden_size, config["hidden_dim"])
        self.context_length = self.bert.config.max_position_embeddings
        self.predictor = ProsodyPredictor(
            style_dim=config["style_dim"], d_hid=config["hidden_dim"],
            nlayers=config["n_layer"], max_dur=config["max_dur"], dropout=config["dropout"]
        )
        self.text_encoder = TextEncoder(
            channels=config["hidden_dim"], kernel_size=config["text_encoder_kernel_size"],
            depth=config["n_layer"], n_symbols=config["n_token"]
        )
        self.decoder = Decoder(
            dim_in=config["hidden_dim"], style_dim=config["style_dim"],
            dim_out=config["n_mels"], disable_complex=disable_complex, **config["istftnet"]
        )

        # tải model nếu chưa có
        if not model:
            model_path = os.path.join(cache_dir, f"{model_name}.pth")
            if not os.path.exists(model_path):
                logger.info(f"Downloading model from Google Drive to {model_path}")
                gdown.download(drive_info["model"], model_path, quiet=False)
            model = model_path

        # load weights
        for key, state_dict in torch.load(model, map_location="cpu").items():
            assert hasattr(self, key), key
            try:
                getattr(self, key).load_state_dict(state_dict)
            except:
                logger.debug(f"Did not load {key} from state_dict")
                state_dict = {k[7:]: v for k, v in state_dict.items()}
                getattr(self, key).load_state_dict(state_dict, strict=False)

    def _download_voices_folder(self):
        """Tải và giải nén folder voices từ Google Drive - CHUẨN"""
        # Nếu đã có voices folder và có file thì thôi
        if os.path.exists(self.voices_dir) and os.listdir(self.voices_dir):
            logger.info(f"✅ Voices folder already exists at {self.voices_dir} "
                        f"({len(os.listdir(self.voices_dir))} files)")
            return

        os.makedirs(self.voices_dir, exist_ok=True)
        zip_path = os.path.join(self.voices_dir, self.VOICES_ZIP["filename"])

        # Nếu đã có voices.zip sẵn trong thư mục chính, copy đường dẫn
        if not os.path.exists(zip_path):
            local_zip = self.VOICES_ZIP["filename"]
            if os.path.exists(local_zip):
                logger.info(f"Found local voices.zip at {local_zip}, using it")
                os.replace(local_zip, zip_path)
            else:
                # Tải từ Google Drive
                logger.info(f"Downloading voices.zip from Google Drive to {zip_path}")
                gdown.download(self.VOICES_ZIP["url"], zip_path, quiet=False)

        # Giải nén
        logger.info(f"Extracting voices.zip to {self.voices_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.voices_dir)

        # Xoá file zip
        os.remove(zip_path)

        # Check kết quả
        files = os.listdir(self.voices_dir)
        if not files:
            logger.warning("⚠️ Voices folder is still empty after extraction!")
        else:
            logger.info(f"✅ Voices extracted successfully with {len(files)} files at {self.voices_dir}")


    @property
    def device(self):
        return self.bert.device

    @dataclass
    class Output:
        audio: torch.FloatTensor
        pred_dur: Optional[torch.LongTensor] = None

    @torch.no_grad()
    def forward_with_tokens(
        self,
        input_ids: torch.LongTensor,
        ref_s: torch.FloatTensor,
        speed: float = 1
    ) -> tuple[torch.FloatTensor, torch.LongTensor]:
        input_lengths = torch.full(
            (input_ids.shape[0],), 
            input_ids.shape[-1], 
            device=input_ids.device,
            dtype=torch.long
        )

        text_mask = torch.arange(input_lengths.max()).unsqueeze(0).expand(input_lengths.shape[0], -1).type_as(input_lengths)
        text_mask = torch.gt(text_mask+1, input_lengths.unsqueeze(1)).to(self.device)
        bert_dur = self.bert(input_ids, attention_mask=(~text_mask).int())
        d_en = self.bert_encoder(bert_dur).transpose(-1, -2)
        s = ref_s[:, 128:]
        d = self.predictor.text_encoder(d_en, s, input_lengths, text_mask)
        x, _ = self.predictor.lstm(d)
        duration = self.predictor.duration_proj(x)
        duration = torch.sigmoid(duration).sum(axis=-1) / speed
        pred_dur = torch.round(duration).clamp(min=1).long().squeeze()
        indices = torch.repeat_interleave(torch.arange(input_ids.shape[1], device=self.device), pred_dur)
        pred_aln_trg = torch.zeros((input_ids.shape[1], indices.shape[0]), device=self.device)
        pred_aln_trg[indices, torch.arange(indices.shape[0])] = 1
        pred_aln_trg = pred_aln_trg.unsqueeze(0).to(self.device)
        en = d.transpose(-1, -2) @ pred_aln_trg
        F0_pred, N_pred = self.predictor.F0Ntrain(en, s)
        t_en = self.text_encoder(input_ids, input_lengths, text_mask)
        asr = t_en @ pred_aln_trg
        audio = self.decoder(asr, F0_pred, N_pred, ref_s[:, :128]).squeeze()
        return audio, pred_dur

    def forward(
        self,
        phonemes: str,
        ref_s: torch.FloatTensor,
        speed: float = 1,
        return_output: bool = False
    ) -> Union['KModel.Output', torch.FloatTensor]:
        input_ids = list(filter(lambda i: i is not None, map(lambda p: self.vocab.get(p), phonemes)))
        logger.debug(f"phonemes: {phonemes} -> input_ids: {input_ids}")
        assert len(input_ids)+2 <= self.context_length, (len(input_ids)+2, self.context_length)
        input_ids = torch.LongTensor([[0, *input_ids, 0]]).to(self.device)
        ref_s = ref_s.to(self.device)
        audio, pred_dur = self.forward_with_tokens(input_ids, ref_s, speed)
        audio = audio.squeeze().cpu()
        pred_dur = pred_dur.cpu() if pred_dur is not None else None
        logger.debug(f"pred_dur: {pred_dur}")
        return self.Output(audio=audio, pred_dur=pred_dur) if return_output else audio

class KModelForONNX(torch.nn.Module):
    def __init__(self, kmodel: KModel):
        super().__init__()
        self.kmodel = kmodel

    def forward(
        self,
        input_ids: torch.LongTensor,
        ref_s: torch.FloatTensor,
        speed: float = 1
    ) -> tuple[torch.FloatTensor, torch.LongTensor]:
        waveform, duration = self.kmodel.forward_with_tokens(input_ids, ref_s, speed)
        return waveform, duration