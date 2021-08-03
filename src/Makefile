init:
	python compile.py
out:
	cat list/*.js js/*.js timeline.js > output.js
copy:
	cat output.js | pbcopy
wav:
	cd audio; python extract-sounds.py  # audio/ にいることを前提とした処理
	python compile.py
all:
	make wav
	python check.py
	make out
	make copy
	cat todo.txt
check:
	python check.py
