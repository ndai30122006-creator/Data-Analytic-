import { datasets } from "../../api/datasets.js";

export const ingest = {
  list: datasets.list,
  upload: datasets.ingestFile,
  profile: datasets.getProfile,
};
