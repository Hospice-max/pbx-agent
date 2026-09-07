# Contributing

1. Fork the repository.
2. Create a branch for the change.
3. Keep changes focused and documented.
4. Do not commit PBX credentials, logs containing personal data, or production configuration.
5. Run:

```bash
python3 -m compileall agent
python3 -m unittest discover -s tests -v
```

6. Open a pull request with a clear description and test results.
