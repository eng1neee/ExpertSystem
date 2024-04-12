import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Candidate(BaseModel):
    name: str
    age: int
    experience: float
    skills: list[str]


class JobOpening(BaseModel):
    position: str
    department: str
    min_experience: float
    required_skills: list[str]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("template.html", {"request": request})


@app.post("/compare_candidates/", response_class=HTMLResponse)
async def compare_candidates(job: JobOpening, candidates: list[Candidate]):
    if not job or not candidates:
        return JSONResponse({"error": "Missing job or candidates data"}, status_code=400)

    best_candidates = []
    best_score = (0, 0, float('inf'))

    for candidate in candidates:
        score = calculate_candidate_score(job, candidate)

        if score > best_score:
            best_candidates = [candidate]
            best_score = score
        elif score == best_score:
            best_candidates.append(candidate)

    if best_candidates:
        output = ""
        for candidate in best_candidates:
            output += f" Name: {candidate.name} "
            output += f" Age: {candidate.age} "
            output += f" Experience: {candidate.experience} "
            output += f" Skills: {', '.join(candidate.skills)} "
        return HTMLResponse(content=output)
    else:
        return JSONResponse({"error": "No best candidate found"}, status_code=404)


def calculate_candidate_score(job: JobOpening, candidate: Candidate) -> tuple:
    experience_score = candidate.experience if candidate.experience >= job.min_experience else 0
    skills_score = sum(1 for skill in job.required_skills if skill in candidate.skills)
    age_score = candidate.age
    return (experience_score, skills_score, age_score)
