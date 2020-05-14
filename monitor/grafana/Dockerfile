FROM alpine/git as downloader

WORKDIR /temp

RUN git clone https://github.com/lightninglabs/lndmon.git

FROM grafana/grafana:6.2.0 as final

COPY --from=downloader /temp/lndmon/grafana/provisioning /etc/grafana/provisioning

COPY --from=downloader /temp/lndmon/grafana/grafana.ini /etc/grafana
