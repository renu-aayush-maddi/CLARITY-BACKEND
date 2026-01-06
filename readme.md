CLARITY – Clinical Lifecycle Analytics for Real-Time Intelligence

clarity\Scripts\activate
uvicorn backend.app.main:app --reload




python -m venv clarity





pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pandas



git checkout -b feature-something
# work
git add .
git commit -m "clear message"
git push
# when done
git checkout main
git merge feature-something
git push
