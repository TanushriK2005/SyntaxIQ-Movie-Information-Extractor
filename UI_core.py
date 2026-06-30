import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_mistralai import ChatMistralAI
import streamlit as st

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineExtract · Movie Intelligence",
    page_icon="🎬",
    layout="centered",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* Reset & base */
html, body, [data-testid="stAppViewContainer"] {
    background: #0A0A0F;
    color: #E8E6E1;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }

/* Hide default Streamlit elements */
#MainMenu, footer { visibility: hidden; }

/* Main container */
.block-container {
    max-width: 780px;
    padding: 2.5rem 2rem 4rem;
}

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    color: #C9A84C;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    line-height: 1.1;
    color: #F0EDE6;
    margin: 0 0 0.6rem;
}
.hero-title em {
    font-style: italic;
    color: #C9A84C;
}
.hero-sub {
    font-size: 1rem;
    color: #8A8A96;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Divider */
.rule {
    border: none;
    border-top: 1px solid #1E1E2A;
    margin: 2rem 0;
}

/* Text area */
[data-testid="stTextArea"] textarea {
    background: #11111A !important;
    border: 1px solid #252535 !important;
    border-radius: 10px !important;
    color: #E8E6E1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.65 !important;
    caret-color: #C9A84C;
    transition: border-color 0.2s;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.12) !important;
}
[data-testid="stTextArea"] label {
    color: #8A8A96 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em;
}

/* Button */
[data-testid="stButton"] button {
    background: #C9A84C !important;
    color: #0A0A0F !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2.2rem !important;
    width: 100%;
    transition: opacity 0.18s, transform 0.12s;
}
[data-testid="stButton"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px);
}

/* Result card */
.result-card {
    background: #11111A;
    border: 1px solid #1E1E2A;
    border-radius: 14px;
    padding: 2rem 2.2rem;
    margin-top: 2rem;
}
.card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.85rem;
    color: #F0EDE6;
    margin: 0 0 0.25rem;
    line-height: 1.15;
}
.card-year {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #C9A84C;
    letter-spacing: 0.12em;
    margin-bottom: 1.2rem;
}
.meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.4rem;
}
.badge {
    background: #1A1A26;
    border: 1px solid #2A2A3A;
    border-radius: 100px;
    font-size: 0.78rem;
    color: #B0AEB8;
    padding: 0.28rem 0.75rem;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.badge.genre {
    border-color: #C9A84C44;
    color: #C9A84C;
}
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    color: #4A4A5A;
    text-transform: uppercase;
    margin: 1.4rem 0 0.5rem;
}
.summary-text {
    font-size: 0.96rem;
    color: #A8A6B0;
    line-height: 1.75;
}
.rating-block {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 1.4rem;
    padding-top: 1.4rem;
    border-top: 1px solid #1E1E2A;
}
.rating-number {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #C9A84C;
    line-height: 1;
}
.rating-label {
    font-size: 0.78rem;
    color: #5A5A6A;
}
.stars {
    font-size: 1rem;
    color: #C9A84C;
    letter-spacing: 2px;
}

/* Error / info banners */
[data-testid="stAlert"] {
    background: #11111A !important;
    border: 1px solid #2A2A3A !important;
    border-radius: 10px !important;
    color: #E8E6E1 !important;
}

/* Spinner */
[data-testid="stSpinner"] { color: #C9A84C; }

/* Example pills */
.example-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.6rem;
}
.example-pill {
    background: #15151F;
    border: 1px solid #252535;
    border-radius: 6px;
    font-size: 0.75rem;
    color: #6A6A7A;
    padding: 0.22rem 0.6rem;
    cursor: default;
}
</style>
""", unsafe_allow_html=True)


# ── LangChain setup ───────────────────────────────────────────────────────────
@st.cache_resource
def build_chain():
    model = ChatMistralAI(model="mistral-small-2603")

    class Movie(BaseModel):
        title: str
        release_year: Optional[int]
        genre: List[str]
        director: Optional[str]
        cast: List[str]
        rating: Optional[float]
        summary: str

    parser = PydanticOutputParser(pydantic_object=Movie)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract movie information from the paragraph\n{format_instructions}"),
        ("human", "{paragraph}"),
    ])
    return model, parser, prompt


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">🎬 &nbsp; AI · Movie Intelligence</div>
  <h1 class="hero-title">Turn text into<br><em>structured cinema data</em></h1>
  <p class="hero-sub">Paste any movie description, review, or article snippet — CineExtract pulls out the details automatically.</p>
</div>
<hr class="rule">
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
paragraph = st.text_area(
    "PASTE YOUR PARAGRAPH",
    placeholder=(
        'e.g. "The Dark Knight (2008), directed by Christopher Nolan, '
        'is a crime thriller featuring Christian Bale and Heath Ledger..."'
    ),
    height=180,
    label_visibility="visible",
)

st.markdown("""
<div class="example-row">
  <span class="example-pill">Movie reviews</span>
  <span class="example-pill">Wikipedia excerpts</span>
  <span class="example-pill">IMDb blurbs</span>
  <span class="example-pill">News articles</span>
</div>
""", unsafe_allow_html=True)

st.write("")
run = st.button("Extract Movie Data →")


# ── Extract & display ─────────────────────────────────────────────────────────
if run:
    if not paragraph.strip():
        st.warning("Please paste a paragraph before extracting.")
    else:
        try:
            model, parser, prompt = build_chain()
            with st.spinner("Analyzing your paragraph…"):
                final_prompt = prompt.invoke({
                    "paragraph": paragraph,
                    "format_instructions": parser.get_format_instructions(),
                })
                response = model.invoke(final_prompt)
                movie = parser.parse(response.content)

            # ── Stars helper ──────────────────────────────────────────────────
            def stars(r):
                if r is None:
                    return ""
                filled = round(r / 2)
                return "★" * filled + "☆" * (5 - filled)

            # ── Genre badges ──────────────────────────────────────────────────
            genre_html = "".join(f'<span class="badge genre">{g}</span>' for g in movie.genre) if movie.genre else ""

            # ── Cast badges ──────────────────────────────────────────────────
            cast_html = "".join(f'<span class="badge">{c}</span>' for c in movie.cast) if movie.cast else '<span class="badge">N/A</span>'

            # ── Director ─────────────────────────────────────────────────────
            director_str = movie.director or "Unknown"

            # ── Year ─────────────────────────────────────────────────────────
            year_str = str(movie.release_year) if movie.release_year else "Year unknown"

            # ── Rating ───────────────────────────────────────────────────────
            rating_section = ""
            if movie.rating is not None:
                rating_section = f"""
                <div class="rating-block">
                  <div>
                    <div class="rating-number">{movie.rating:.1f}</div>
                    <div class="stars">{stars(movie.rating)}</div>
                  </div>
                  <div class="rating-label">Rating out of 10</div>
                </div>"""

            st.markdown(f"""
            <div class="result-card">
              <div class="card-year">{year_str}</div>
              <div class="card-title">{movie.title}</div>

              <div class="section-label">Genre</div>
              <div class="meta-row">{genre_html if genre_html else '<span class="badge">N/A</span>'}</div>

              <div class="section-label">Director</div>
              <div class="meta-row"><span class="badge">{director_str}</span></div>

              <div class="section-label">Cast</div>
              <div class="meta-row">{cast_html}</div>

              <div class="section-label">Summary</div>
              <p class="summary-text">{movie.summary}</p>

              {rating_section}
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Extraction failed: {e}")