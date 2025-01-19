# Cycle Stats Service

## Initialize
1. `echo -n <strava_client_id> > strava_client_id.txt`
2. `echo -n <strava_client_secret> > strava_client_secret.txt`
3. `echo -n <strava_refresh_token> > strava_refresh_token.txt`

Equivalent For Windows
1. Out-File -FilePath .\strava_client_id.txt -InputObject "<strava_client_id>" -Encoding ascii -NoNewline
2. $env:STRAVA_CLIENT_ID_FILE="strava_client_id.txt"
3. $env:STRAVA_CLIENT_SECRET_FILE="strava_client_secret.txt"
4. $env:STRAVA_REFRESH_TOKEN_FILE="strava_refresh_token.txt"


## Run
`PORT=9000 docker-compose up -d --build`

## Test
`curl -v localhost:9000/api/v1/cycle`
