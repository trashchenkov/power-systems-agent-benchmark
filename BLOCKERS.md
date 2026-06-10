# BLOCKERS.md

No blockers yet.


## 2026-06-08T06:40:17.355603+00:00 — Google Drive folder is very broad

Folder `16KLAlLYdT9UR3eCPPOt29f8YAnB7juGw` is accessible, but appears to be a broad personal `Documents` tree rather than a curated literature folder. Attempting to download the whole folder via gdown ran for 10 minutes and timed out after downloading only 23 files / 48.5 MB, mostly unrelated setup/Arduino/admin/course-material files. A recursive no-download listing later succeeded and found 8,439 downloadable files, confirming that useful material exists deep in nested folders. The blocker is not access/listing anymore; it is avoiding root-wide download and instead doing selective downloads from high-signal subtrees such as `мероприятия/Эстония/стажировка/microgrid/`, `related papers`, `reliability data`, and nested power-systems course PDFs.
