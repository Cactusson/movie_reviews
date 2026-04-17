# Movie Reviews

Collects movie reviews from different websites into a single place.

## How to Run

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Start the project with Docker Compose:

```bash
docker compose up
```

The application will be available at http://localhost:8000.

For the first time setup run the following commands:

```bash
# populate the database with movie reviews (this might take a while)
docker compose exec web python src/manage.py collect_reviews --init

# turn on automatic hourly collection
docker compose exec web python src/manage.py start
```

## How to Run Tests

```bash
docker compose exec web bash -c "cd src && pytest"
```

## Management Commands

To run a command:

```bash
docker compose exec web python src/manage.py <command>
```

Available commands:

+ `start` : Turns on the aggregator which is then going to collect movie reviews every hour (it's turned off by default).
+ `stop` : Turns off the aggregator.
+ `status` : Displays the current status of the aggregator.
+ `collect_reviews` : Collects reviews manually.
  - Without `--init`: Only fetches reviews from the last week.
  - With `--init`: Fetches reviews up to the `CUTOFF_YEAR` (2015 by default, you can change it in `settings.py`).
