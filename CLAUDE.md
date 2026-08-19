# Academic website — maintenance notes

Personal academic site of Shixin Zheng (郑仕欣), Postdoctoral Associate, Department of
Mathematics, University of Maryland, College Park.

- Live: <https://shixin-zheng.github.io>
- Repo: `shixin-zheng/shixin-zheng.github.io` (branch `master`)
- Engine: Jekyll (academicpages template), deployed by `.github/workflows/jekyll.yml`
  on every push to `master`. Nothing to build or deploy by hand.

## Source of truth

Content comes from `~/research`, **not** from memory or the web:

| Site content | Authoritative source |
| --- | --- |
| The CV PDF at `/files/CV_Shixin_Zheng.pdf` | `cv-src/CV_Shixin_Zheng.tex` **in this repo** — edit it, then run `./cv-src/build.sh` (needs `tectonic`) |
| CV facts (education, appointments, publications, funding, service, honors, talks) | `~/research/NIW/CV/CV_Shixin_Zheng_NIW.tex` — the longer CV variant, kept current by the user |
| Older CV variant | `~/research/AMSTravelFund/CV_Shixin_Zheng.tex` |
| Paper titles, abstracts, arXiv numbers | the project's `overleaf/` directory under `~/research/<project>/` |
| Ongoing / unpublished work | `~/research/<project>/{topics,wiki,meetings}` — treat as private until it is on arXiv |

Active project directories follow the layout `ideas/ meetings/ overleaf/ topics/ wiki/
workspace/` (e.g. `Riemannian-GPE`, `bm-stratified-opt`, `curse-of-dim`, `imuon-prior`,
`imuon-followup`, `Daytrader-RL`). Numbered `projectN(...)` directories are older work.

**Never invent a publication, talk, award, or service item.** If it is not in the CV tex or
in a paper under `~/research`, ask before putting it on the site.

## Layout

- `_pages/about.md` — homepage; also carries the full publication list by hand.
- `_pages/cv.md` — CV page; links to `files/CV_Shixin_Zheng.pdf`.
- `_publications/YYYY-MM-DD-slug.md` — one file per paper. `category:` must be one of the
  keys under `publication_category` in `_config.yml` (`manuscripts`, `preprints`,
  `conferences`, `books`); a category not listed there silently disappears from
  `/publications/`.
- `_talks/`, `_teaching/` — one file per talk / course.
- `_config.yml` — identity, social links, collection settings.

Adding a paper means touching **both** `_publications/` and the list in `_pages/about.md`,
and usually `files/CV_Shixin_Zheng.pdf`.

## Conventions

- American English throughout (see the user's global preferences).
- Author name is bolded as `**S. Zheng**` in the about-page publication list.
- Publications carry DOI/journal links when published, arXiv links always.
- The public CV (`cv-src/CV_Shixin_Zheng.tex`) is deliberately shorter than the NIW CV in
  `~/research`: it omits research funding, citation metrics, the dissertation entry, and
  technical skills. Keep the facts consistent between the two, not the section lists.
  Originally authored as `~/Jobs/02-resume/cv-academic.tex`; this repo is now the master
  copy for the *website* CV.
- `author.github` in `_config.yml` points to **ZhengShixin**, the user's main GitHub
  account. `shixin-zheng` is a secondary account that exists only to host this site — do
  not "correct" the profile link to it.

## Local preview

The system Ruby (2.6) has no Jekyll installed, so there is no working local preview yet.
Either `bundle install` with a newer Ruby, or use `docker-compose up` (see `Dockerfile`),
before promising a rendered check.
