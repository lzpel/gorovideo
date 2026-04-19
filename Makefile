.PHONY: run build install clean

generate:
	cd web && npm ci

run:
	cd web && npm run dev

deploy:
	cd web && npm run build

clean:
	rm -rf web/.next web/out
