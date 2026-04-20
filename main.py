# main.py

import re
from tempfile import template

from fastapi import Depends, FastAPI, Request
from fastapi.params import Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db



# fastapi 객체 생성
app = FastAPI()

#jinja2 템플릿 객체 생성 (templates 파일들이 어디에 있는지 알려야 한다.)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request:Request):
	return templates.TemplateResponse(
		request=request,
		name="index.html",
		context={
			"fortuneToday":"동쪽으로 가면 귀인을 만나요"
		}
	)

@app.get("/post", response_class=HTMLResponse)
def getPost(request:Request, db:Session = Depends(get_db)):
	# DB에서 글 목록을 가져오기 위한 sql 문 준비
	query=text("""
		SELECT num, writer, title, content, created_at
		FROM post
		ORDER BY num DESC
	""")

	# 글 목록을 얻어와
	result = db.execute(query)
	posts = result.fetchall()

	# 응답하기
	return templates.TemplateResponse(
		request=request,
		name="post/list.html", # templates/post/list.html jinja2를 해석한 결과를 응답
		context={
			"posts":posts
		}
	)

@app.get("/post/new", response_class=HTMLResponse)
def getNew(request:Request):
	return templates.TemplateResponse(request=request, name="post/new-form.html")

@app.post("/post/new")
def postNew(writer: str=Form(...), title: str=Form(...), content: str=Form(...),
			db: Session=Depends(get_db)):
	
	# DB에 저장할 sql 문
	query = text("""
		INSERT INTO post
			  (writer, title, content)
		VALUES
			  (:writer, :title, :content)
	""")
	db.execute(query, {"writer":writer, "title":title, "content":content})
	db.commit()

	# 정보 저장 후 특정 경로로 리다이렉트
	return RedirectResponse("/post", status_code=302)

@app.post("/post/delete")
def delete_post(num: int = Form(...), db: Session = Depends(get_db)):

    query = text("""
        DELETE FROM post
        WHERE num = :num
    """)

    db.execute(query, {"num": num})
    db.commit()

    return RedirectResponse("/post", status_code=302)
