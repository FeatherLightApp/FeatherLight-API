FROM alpine

RUN apk --update add curl jq git 

WORKDIR /download

RUN git clone https://github.com/lightninglabs/lndmon.git

RUN cp /download/lndmon/post_start/script/set_default_graf_dash.sh /bin/

RUN chmod +x /bin/set_default_graf_dash.sh

CMD set_default_graf_dash.sh