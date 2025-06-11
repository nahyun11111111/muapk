from flask import Flask, render_template # Flask와 render_template 함수를 가져옵니다.

app = Flask(__name__) # Flask 앱을 생성합니다.

# 기본 경로 '/'로 접속했을 때 실행될 함수를 정의합니다.
@app.route('/')
def home():
    return render_template('index.html') # templates 폴더의 index.html 파일을 렌더링하여 반환합니다.

# 이 파일이 직접 실행될 때 Flask 앱을 실행합니다.
if __name__ == '__main__':
    app.run(debug=True) # debug=True는 개발 중에는 편리하지만, 실제 서비스에서는 False로 해야 합니다.