PYTHON=python3
TARGET ?= targets/example.txt
FLAGS ?= --output results.txt
.PHONY: run install help
run:
	sudo $(PYTHON) -m src.main $(TARGET) $(FLAGS)
install:
	$(PYTHON) -m pip install --break-system-packages -r requirements.txt
help:
	@echo "Usage:"
	@echo "  make run"
	@echo "  make run TARGET=targets/example.txt"
	@echo "  make run FLAGS=\"--output results.txt -n\""
