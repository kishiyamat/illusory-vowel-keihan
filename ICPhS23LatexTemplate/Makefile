pdf:
	cp icphs2023-template.tex template.tex
	rm -f template.blg
	rm -f template.bbl
	rm -f template.aux
	rm -f mybib.bib
	curl https://raw.githubusercontent.com/kishiyamat/bibliography/master/bibliography.bib > mybib.bib
	pdflatex template.tex
	pbibtex template
	pdflatex template.tex
	pdflatex template.tex
	# make clean

embed:
	# 埋め込み
	## GS
	# gs -q -dNOPAUSE -dBATCH -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite -sOutputFile=tmp.pdf paper.pdf
	# mv tmp.pdf paper.pdf
	## Interspeech
	pdf2ps template.pdf
	ps2pdf -dPDFSETTINGS=/prepress template.pdf 
	mv template.pdf.pdf template.pdf  # fixme
	rm template.ps
	# check
	pdffonts template.pdf

