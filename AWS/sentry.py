import sentry_sdk
sentry_sdk.init(
    "https://863cc4475bea402abbad256bae2de40c@o510423.ingest.sentry.io/5606062",
    traces_sample_rate=1.0
)

division_by_zero = 1 / 0
