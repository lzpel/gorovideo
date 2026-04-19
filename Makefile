.PHONY: run build install clean

run:
	cd web && npm run dev

build:
	cd web && npm run build

install:
	cd web && npm ci

clean:
	rm -rf web/.next web/out
