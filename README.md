# Cycle Stats Service

## Initialize
1. `echo -n <strava_client_id> > strava_client_id.txt`
2. `echo -n <strava_client_secret> > strava_client_secret.txt`
3. `echo -n <strava_refresh_token> > strava_refresh_token.txt`

## Run
`PORT=9000 docker-compose up -d --build`

## Test
`curl -v localhost:9000/api/v1/cycle`
