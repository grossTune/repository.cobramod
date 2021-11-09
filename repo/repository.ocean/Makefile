.DEFAULT_GOAL := default
proj = "repository.ocean"
version = "0.0.1"

default:
	git archive --prefix=$(proj)/ master -o $(proj)-$(version).zip
	cp $(proj)-$(version).zip $(proj)-latest.zip
