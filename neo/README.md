The following is the process you need to follow when starting a fresh terminal:

1. Run cd "/neofs-dev-env"
2. Run make get
3. Run make hosts
4. Run make up
5. Run the following at once:
	export NEOFS_ENDPOINT="s01.neofs.devenv:8080"
	export NEOFS_WALLET="./wallets/wallet.json"
	export NEOFS_CONTAINER_ID="2xsGgxv9GMTFpbXwRDPaZrywzKzoe1he2W7PyptY7Ejk"
	export NEOFS_CLI_PATH="/bin/neofs-cli"
6. Finally just run VSCode script normally

(base) manuel-jardim@manuel-jardim-VivoBook:~/Documents/hackathon/neo/NeoFS/neofs-dev-env$ neofs-cli container create \
  --rpc-endpoint "$NEOFS_ENDPOINT" \
  --wallet "$NEOFS_WALLET" \
  --policy "REP 1" \
  --basic-acl private \
  --await
Enter password > 
container has been persisted on FS chain
container ID: E3U1vNvbdfKBoSUtp47oZcCrspxMvTbnw2h1B9QjZFVK