<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />



**Dead Pixel Forensics** 🎯


## Basic Details
### Team Name: Srishti


### Team Members
- Member 1: Shreya Suja Sukumaran - Jyothi Engineering College(Autonomous)
- Member 2: Ayisha Begam - Jyothi Engineering College(Autonomous)

### Project Description
The project basically analyses a screen display that has been showing pink/blue/green line issues, our system counts the total number of lines, their intersections, percentage it can be repaired etc.

### The Problem (that doesn't exist)
Difficulty in counting and identifying the total number of lines and colors of lines

### The Solution (that nobody asked for)
The system upon taking the input image of a damaged screen display counts the total number of lines, lines of each color, which is in majority, etc.

## Technical Details
### Software
Languages

Python 3.11+ — backend processing, computer vision pipeline
JavaScript (ES2022) — frontend application logic
CSS3 — styling and animations
HTML5 — markup
Frameworks

FastAPI ≥0.110 — REST API server (Python)
React ^19 — frontend UI framework
Vite ^8.3 — frontend build tool and dev server

# Screenshots
<img width="1920" height="1020" alt="Screenshot 2026-09-12 031638" src="https://github.com/user-attachments/assets/c0666e55-5e3c-4ec2-abea-92b4e60717d2" />
*Welcome page of the website*

<img width="1920" height="1020" alt="Screenshot 2026-09-12 030936" src="https://github.com/user-attachments/assets/1a4ac63e-8f7d-4cc3-a8ae-615c3bbcf59c" />
*Page to upload image*

<img width="1920" height="1020" alt="Screenshot 2026-09-12 031002" src="https://github.com/user-attachments/assets/99f70f56-e4e9-41cf-a12c-26e9662110a9" />
*page after image analysis*

<img width="1920" height="1020" alt="Screenshot 2026-09-12 031012" src="https://github.com/user-attachments/assets/0d8a55f8-dcce-4b81-ad93-87474aeaed8b" />
*result analysis part 1*

<img width="1920" height="1020" alt="Screenshot 2026-09-12 031019" src="https://github.com/user-attachments/assets/50009a9d-b32c-43ab-a30e-b73bccf32db9" />
*result analysis part 2*

<img width="1920" height="1020" alt="Screenshot 2026-09-12 031032" src="https://github.com/user-attachments/assets/d66357fd-95f0-4609-9304-d55afcd46ed4" />
*result analysis part 3*

# Diagrams
<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/6e040a24-9b4a-42ce-a34b-5490bd30c0de" />

*The workflow starts with a damaged screen image uploaded through the React + Vite frontend. The image is analyzed by the FastAPI backend using four computer vision stages: preprocessing, line detection, per-line analysis, and pixel analysis. The extracted results are used to calculate the Repairability Index and Symmetry Score, which are then generated as JSON, annotated PNG, and PDF outputs for display on the dashboard.*

### Project Demo
# Video


https://github.com/user-attachments/assets/2c2d16d8-cd79-42e3-a5c9-3d7301f45600








## Team Contributions
- Shreya Suja Sukumaran: Frontend & UI Development

Developed the React + Vite frontend.
Designed the image upload interface and interactive dashboard.
Integrated the frontend with the FastAPI backend using the /api/analyze API.
Displayed analysis results, damage information, and generated reports.

- Ayisha Begam: Backend & Computer Vision

Developed the FastAPI backend and image-analysis API.
Implemented the computer vision pipeline for screen damage detection.
Worked on preprocessing, line detection, per-line analysis, and pixel analysis.
Developed the Metrics Engine to calculate the Repairability Index and Symmetry Score.
Implemented generation of JSON results, annotated images, and PDF reports.

---
Made with ❤️ at TinkerHub Useless Projects 

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)



