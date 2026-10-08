## Starting MediaGrab Server Components

### Web Application (Next.js)
To start the web application:
1. Navigate to the web directory: `cd /home/null/projects/MediaGrab/web`
2. Run: `npm run dev`
3. Access at http://localhost:3001 (or the port shown in the terminal)

### FastAPI Server
To start the FastAPI server, you would need to:

1. Navigate to the server directory: `cd /home/null/projects/MediaGrab/server`
2. If using Python (with pip available): 
   - Install dependencies: `pip install -r requirements.txt`
   - Run the server: `python3 app/main.py` or `uvicorn app.main:app --host 0.0.0.0 --port 8000`

3. If using Docker (preferred method):
   - Build the image: `docker build -t media-grab-server .`
   - Run the container: `docker run -p 8000:8000 media-grab-server`

The web application is configured to look for the API at http://localhost:8000 by default, which matches what's indicated in the code in `/home/null/projects/MediaGrab/web/src/app/page.tsx`.