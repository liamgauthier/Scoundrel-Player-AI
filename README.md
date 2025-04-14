# Scoundrel-Player-AI
A Reinforcement model that plays the solitaire game "Scoundrel" by Zach Gage and Kurt Bieg

Rules can be found [here](http://stfj.net/art/2011/Scoundrel.pdf).

## To play the game yourself:

 - download the latest version of python
 - install dependencies by running the following in your command line:
   ```
   pip install "fastapi[standard]"
   pip install pydantic
   pip install starlette
   pip install uvicorn
   ```
 - run the API by running the following in your command line:
   ```
   fastapi dev main.py
   ```
 - go to [http://127.0.0.1:8000/scoundrel/](http://127.0.0.1:8000/scoundrel/)
