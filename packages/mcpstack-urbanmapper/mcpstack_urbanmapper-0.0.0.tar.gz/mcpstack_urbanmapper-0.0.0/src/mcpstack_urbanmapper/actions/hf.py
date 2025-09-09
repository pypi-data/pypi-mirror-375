from __future__ import annotations


def um_hf_dataset_schema(
    repo_id: str, split: str = "train", sample_size: int = 10
) -> dict:
    out: dict = {"repo_id": repo_id, "split": split}
    try:
        from datasets import load_dataset, load_dataset_builder

        builder = load_dataset_builder(repo_id)
        info = builder.info
        out["description"] = getattr(info, "description", None)
        out["features"] = {
            k: str(v) for k, v in (getattr(info, "features", {}) or {}).items()
        }
        try:
            ds = load_dataset(repo_id, split=split, streaming=True)
            head = []
            for i, row in enumerate(ds):
                head.append({k: (str(v)[:200]) for k, v in row.items()})
                if i + 1 >= sample_size:
                    break
            out["sample_rows"] = head
        except Exception:
            ds = load_dataset(repo_id, split=split)
            out["columns"] = list(ds.column_names)
            out["sample_rows"] = [ds[i] for i in range(min(sample_size, len(ds)))]
        cols = set(out.get("features", {}).keys()) | set(out.get("columns", []) or [])
        cols |= set(out["sample_rows"][0].keys()) if out.get("sample_rows") else set()
        lc = {c.lower(): c for c in cols}
        guess = {}
        for cand in ["longitude", "lon", "lng", "x"]:
            if cand in lc:
                guess["longitude_column"] = lc[cand]
                break
        for cand in ["latitude", "lat", "y"]:
            if cand in lc:
                guess["latitude_column"] = lc[cand]
                break
        for cand in ["geometry", "geom", "wkt"]:
            if cand in lc:
                guess["geometry_column"] = lc[cand]
                break
        for cand in ["address", "addr", "street_address"]:
            if cand in lc:
                guess["address_column"] = lc[cand]
                break
        out["inferred_columns"] = guess
        return out
    except Exception as e:
        return {"repo_id": repo_id, "split": split, "error": str(e)}
