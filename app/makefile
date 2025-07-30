update-app:
	rm -r konsul_backend && \
	git clone https://github.com/KirillApasnuy/konsul_backend.git && \
	cd konsul_backend && \
	docker stop fastapi_app && \
	docker compose up --build -d fastapi
