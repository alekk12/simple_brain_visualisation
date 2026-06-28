import sys
import os
import re
import json
import torch
import torch.nn.functional as F
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from transformers import AutoTokenizer, AutoModel
from nilearn import datasets, plotting, image
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import Patch

def get_bert_embedding(text, tokenizer, model, device="cuda"):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    token_embeddings = outputs.last_hidden_state
    mask = inputs["attention_mask"].unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * mask, 1)
    sum_mask = torch.clamp(mask.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def load_atlas(atlas_type, data_dir="../data"):
    if atlas_type == "schaefer":
        atlas = datasets.fetch_atlas_schaefer_2018(n_rois=200, data_dir=data_dir)
        return atlas.maps, atlas.labels, None, None
    elif atlas_type == "aal":
        img_path = os.path.join(data_dir, "AAL3v1.nii")
        lbl_path = os.path.join(data_dir, "AAL3v1.txt")
        with open(os.path.join(data_dir, "AAL3v1.json"), 'r') as f:
            atl_dict = json.load(f)
        img = nib.load(img_path)
        with open(lbl_path, "r") as f:
            labels = [re.sub(r'\d+','',line).strip() for line in f.readlines()]
        indices = [int(i) for i in range(1, len(labels) + 1)]
        return img, labels, atl_dict, indices
    raise ValueError("Atlas type not yet implemented")

import torch

def is_clean(text):
    """proritize full name of the region, not abbreviations. Returns True if the text does not contain underscores or hyphens"""
    return '_' not in text and '-' not in text

def compute_label_embeddings_optimized(labels, atl_dict, tokenizer, model, device="cuda"):
    """computes label embeddings - all synonyms"""
    label_embeddings = []
    
    for label in labels:
        terms = [label]
        weights = [1.5 if is_clean(label) else 0.5]
        if label in atl_dict and 'synonyms' in atl_dict[label]:
            for syn in atl_dict[label]['synonyms']:
                terms.append(syn)
                weights.append(1.5 if is_clean(syn) else 0.5)
        term_embeds = [get_bert_embedding(t, tokenizer, model, device) for t in terms]
        stacked = torch.cat(term_embeds, dim=0)
        w = torch.tensor(weights, device=device).unsqueeze(1)
        weighted_embed = torch.sum(stacked * w, dim=0) / torch.sum(w)
        label_embeddings.append(weighted_embed.unsqueeze(0))
        
    return torch.cat(label_embeddings, dim=0)

def find_top_n_regions(query, tokenizer, model, label_embs, atlas_labels, n=3, device="cuda"):
    query_emb = get_bert_embedding(query, tokenizer, model, device)
    sims = F.cosine_similarity(query_emb, label_embs)
    top_vals, top_indices = torch.topk(sims, n)
    return [(atlas_labels[i], top_vals[j].item(), i) for j, i in enumerate(top_indices)]

def visualize_probabilistic_results(top_results, atlas_maps, atlas_indices, out_path="../output/output.png"):
    #TO DO fix hardcoed paths
    num_regions = len(top_results)
    cmap = plt.colormaps["tab10"].resampled(num_regions)
    data = atlas_maps.get_fdata()
    label_map = np.zeros_like(data, dtype=int)
    label_map = label_map.astype(np.int32)

    for i, (_, _, idx) in enumerate(top_results):
        mask = (atlas_maps.get_fdata() == atlas_indices[idx]) if atlas_indices else (atlas_maps.get_fdata() == idx + 1)
        label_map[mask] = i + 1

    final_img = image.new_img_like(atlas_maps, label_map)
    fig = plt.figure(figsize=(12, 6))
    plotting.plot_roi(
        final_img,
        figure=fig,
        title=f"Top {num_regions} Predicted",
        cmap=cmap,
        colorbar=False
    )
    handles = [Patch(color=cmap(i)) for i in range(num_regions)]
    labels = [f"{r[0]} ({r[1]:.2f})" for r in top_results]
    fig.legend(handles, labels, loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig.savefig(out_path, bbox_inches="tight", dpi=300)
    plt.close(fig)

def load_model(model_path="../biobert",emb_path=Path("../models/embeddings.npy"), comp=False,atlas_type="aal",top_reg=5):
    """load model either from weights or fetch"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    atlas_maps, atlas_labels, atl_dict, atlas_indices = load_atlas(atlas_type)
    tok = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path).to(device)

    if emb_path.is_file():
        embs = np.asarray(np.load(emb_path, mmap_mode="r"))
        embs = torch.from_numpy(embs).float()
        embs = embs.to(device)
    else:
        embs= compute_label_embeddings_optimized(atlas_labels, atl_dict,tok, model, device)
        np.save(emb_path, embs.cpu().numpy())
    print("model loaded", flush=True)
    return model, tok, embs, atlas_maps, atlas_labels, atlas_indices  # replace with real model

def generate(model, tokenizer, embs, atlas_maps, atlas_labels, atlas_indices, query, top_reg=5):
    """save the image to output, return top 1 result"""
    top_result = find_top_n_regions(query, tokenizer, model, embs, atlas_labels, n=top_reg)
    visualize_probabilistic_results(top_result, atlas_maps, atlas_indices)
    return top_result[0]

model, tok, embs, atlas_maps, atlas_labels, atlas_indices = load_model()
for line in sys.stdin:
    req = json.loads(line)
    text = req["text"]
    if len(text) > 1:
        result = generate(model, tok, embs, atlas_maps, atlas_labels, atlas_indices, text)
        print(json.dumps({"result": f"{result[0]} with prob={result[1]}"}), flush=True)