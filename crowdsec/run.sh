#!/usr/bin/with-contenv bashio

bashio::log.info "Running Crowdsec addon"

# Get all arguments
acquisition=$(bashio::config 'acquisition')
collections=$(bashio::config 'collections')
parsers=$(bashio::config 'parsers')
scenarios=$(bashio::config 'scenarios')
postoverflows=$(bashio::config 'postoverflows')
parsers_to_disable=$(bashio::config 'parsers_to_disable')
scenarios_to_disable=$(bashio::config 'scenarios_to_disable')
disable_online_api=$(bashio::config 'disable_online_api')

# Copy Crowdsec config and data files to make it persistent if it's not already
if [ -d "/config/.storage/crowdsec/config/" ]; then
    echo "Crowdsec config directory already persistent..."
else
    mkdir -p /config/.storage/crowdsec/config/
    cp -r /etc/crowdsec/* /config/.storage/crowdsec/config/
    for elem in $(find /config/.storage/crowdsec/config/ -type l); do
        oldlink=$(readlink $elem)
        if [[ "$oldlink" == *"/config/.storage/"* ]]; then
            continue
        else
            newlink="${oldlink//\/etc\/crowdsec/\/config\/.storage\/crowdsec\/config}"
            ln -sf ${newlink} $elem
        fi
    done
    sed -i 's#/etc/crowdsec/#/config/.storage/crowdsec/config/#g' /config/.storage/crowdsec/config/config.yaml
fi
if [ -d "/config/.storage/crowdsec/data/" ]; then
    echo "Crowdsec data directory already persistent..."
else
    mkdir -p /config/.storage/crowdsec/data/
    cp -r /var/lib/crowdsec/data/* /config/.storage/crowdsec/data/
    sed -i 's#/var/lib/crowdsec/data/#/config/.storage/crowdsec/data/#g' /config/.storage/crowdsec/config/config.yaml
fi

# Set acquis.yaml file
echo "${acquisition}" > /config/.storage/crowdsec/config/acquis.yaml

## Environment variables settings
# Disable or not the Online API
if bashio::var.true "${disable_online_api}"; then
    echo "DISABLE ONLINE API..."
    yq eval -i '.api.server.online_client = {"credentials_path": ""}' /config/.storage/crowdsec/config/config.yaml
    #export DISABLE_ONLINE_API="true"
else
    yq eval -i '.api.server.online_client = {"credentials_path": "/config/.storage/crowdsec/config/online_api_credentials.yaml"}' /config/.storage/crowdsec/config/config.yaml
    if ! bashio::fs.file_exists "/config/.storage/crowdsec/config/online_api_credentials.yaml"; then
        cscli -c /config/.storage/crowdsec/config/config.yaml capi register > /config/.storage/crowdsec/config/online_api_credentials.yaml
        echo "Registration to online API done"
    fi
fi

# Set collections to install env var
COLLECTIONS=""
if [[ ! -z "${collections}" ]]; then
    for item in "${collections}"; do
        COLLECTIONS="${COLLECTIONS}${item} "
    done
    export COLLECTIONS="${COLLECTIONS}"
fi

# Set parsers to install env var
PARSERS=""
if [[ ! -z "${parsers}" ]]; then
    for item in "${parsers}"; do
        PARSERS="${PARSERS}${item} "
    done
    export PARSERS="${PARSERS}"
fi

# Set scenarios to install env var
SCENARIOS=""
if [[ ! -z "${scenarios}" ]]; then
    for item in "${scenarios}"; do
        SCENARIOS="${SCENARIOS}${item} "
    done
    export SCENARIOS="${SCENARIOS}"
fi

# Set scenarios to install env var
POSTOVERFLOWS=""
if [[ ! -z "${postoverflows}" ]]; then
    for item in "${postoverflows}"; do
        POSTOVERFLOWS="${POSTOVERFLOWS}${item} "
    done
    export POSTOVERFLOWS="${POSTOVERFLOWS}"
fi

#Set parsers to disable en var
DISABLE_PARSERS=""
if [[ ! -z "${parsers_to_disable}" ]]; then
    for item in "${parsers_to_disable}"; do
        DISABLE_PARSERS="${DISABLE_PARSERS}${item} "
    done
    export DISABLE_PARSERS="${DISABLE_PARSERS}"
fi

#Set scenarios to disable en var
DISABLE_SCENARIOS=""
if [[ ! -z "${scenarios_to_disable}" ]]; then
    for item in "${scenarios_to_disable}"; do
        DISABLE_SCENARIOS="${DISABLE_SCENARIOS}${item} "
    done
    export DISABLE_SCENARIOS="${DISABLE_SCENARIOS}"
fi

exec bash /docker_start.sh
