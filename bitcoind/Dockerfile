
# Start a new image
FROM alpine:latest

LABEL maintainer="Sean Aye <sean.aye2@gmail.com>"

# Expose mainnet ports (server, rpc)
EXPOSE 8333 8334

# Expose testnet ports (server, rpc)
EXPOSE 18333 18334

# Expose simnet ports (server, rpc)
EXPOSE 18555 18556

# Expose segnet ports (server, rpc)
EXPOSE 28901 28902

# COPY "start-btcctl.sh" .
COPY "start-bitcoind.sh" .

RUN apk add --upgrade && \
    apk add --no-cache \
    bash \
    bitcoin \
&&  mkdir "/root/.bitcoind" "/root/.btcctl" \
# &&  chmod +x start-btcctl.sh \
&&  chmod +x start-bitcoind.sh 

COPY bitcoind.conf /root/.bitcoind/bitcoind.conf


# Manually generate certificate and add all domains, it is needed to connect
# "btcctl" and "lnd" to "bitcoind" over docker links.
# RUN openssl req -x509 -newkey rsa:4096 -keyout /rpc/rpc.key -out /rpc/rpc.cert -days 365 -nodes -subj '/CN=btcd'

# Create a volume to house pregenerated RPC credentials. This will be
# shared with any lnd, btcctl containers so they can securely query btcd's RPC
# server.
# You should NOT do this before certificate generation!
# Otherwise manually generated certificate will be overridden with shared
# mounted volume! For more info read dockerfile "VOLUME" documentation.
# VOLUME ["/rpc"]

CMD [ "./start-bitcoind.sh" ]
