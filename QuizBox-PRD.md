# PRD: QuizBox - Auth-Enabled Educational Quiz App (Teaching-Focused)

## Overview
**QuizBox** is a simple, educational web application built to support a beginner Python course. It allows users to log in, create their own quizzes or flashcards, view quizzes created by an admin, and explore Python concepts through realistic data structures and API usage. The application introduces light user authentication, basic session handling, and the ability to interact with structured and nested data through a clean REST API. 

The system will be kept as simple as possible while still showcasing real-world patterns like login, session-based UI, and authenticated API usage.

---

## Goals
- Help students understand how Python is used in real applications
- Allow each user to create and view their own content (safe from profanity concerns)
- Provide default content from an "admin" user to learn from
- Offer structured data formats (nested lists/dictionaries) for API practice
- Keep the architecture minimal and clear (ideal for beginners)

---

## Stack & Architecture

### Backend
- **Flask** (simple route-based architecture)
- **MySQL** with raw SQL (no ORM or migrations)
- **Session-based auth using Flask's built-in session management**
- **API key for API access** via `x-api-key` header (linked to logged-in user)

### Frontend
- Plain HTML/CSS/JS
- **Bootstrap** for styling
- No frontend framework (React, Vue, etc.)
- Communicates with backend using `fetch()` calls

### Deployment
- Docker + Docker Compose (services: backend, frontend, mysql)
- Designed for deployment on low-resource cloud server (1GB RAM)

---

## Features

### Authentication
- `POST /register` — Register with name, email, password
- `POST /login` — Logs user in, stores session
- `GET /logout` — Logs user out, clears session
- `GET /me` — Returns user info (used by frontend)
- `GET /me/api-key` — Returns user's API key for use in headers

### Quizzes / Flashcards
- `POST /quiz` — Create a new quiz item (requires API key)
- `GET /quiz/mine` — Fetch all quizzes created by current user
- `GET /quiz/default` — Fetch admin-created/default quizzes
- `GET /quiz/<id>` — View full detail of a quiz (question, answer, etc.)

### Themes & Topics
- `GET /themes` — List all themes (e.g., Python Strings)
- `GET /themes/<id>/quiz` — Fetch quizzes within a theme

### Advanced Data Structures
- Some quizzes will return nested data (e.g., multiple-answer quizzes, embedded hints, code examples)
- Will help demonstrate parsing JSON, lists, and dictionaries in Python

### User Overview (Optional for Instructor Tools)
- `GET /users` — List users (name only)
- `GET /users/<id>/stats` — Show # of quizzes created, themes used, etc.

---

## Frontend Pages
- Login Page (email + password)
- Register Page
- Dashboard ("My Quizzes")
- Admin Content ("Default Quizzes")
- New Quiz Form
- Logout Button

### Optional Frontend (Stretch Goals)
- Password reset flow (via code, no email integration required)
- Email confirmation (skipped unless requested)

---

## Database Schema

### users
| id | name | email | password_hash | api_key | created_at |

### quizzes
| id | user_id | question_text | answer_text | structure (JSON) | topic | theme_id | created_at |

### themes
| id | name | description |

### api_keys
| id | user_id | api_key | created_at |

---

## Simplicity & Teaching Constraints
- Use Flask session cookies for login/logout
- Use API key (`x-api-key`) to scope API access
- No advanced email integration
- Raw SQL only (no ORM, no migrations)
- Minimal but safe input validation
- No public profanity filtering needed (private scope)

---

## Teaching Integration
- During early Python lessons, use examples from `GET /quiz/default` to teach data parsing
- Introduce loops, conditionals, dict/list access, and nested data handling via quiz objects
- Later show authenticated API usage with `fetch()` and user-created content
- Structure supports future Bootcamp or advanced features without needing rework

---

## Stretch Goals (Optional Later)
- Leaderboard by completion count
- Quiz completion tracking per user
- Tagging, difficulty level, sorting
- User profile & stats page
- Quiz of the Day module
