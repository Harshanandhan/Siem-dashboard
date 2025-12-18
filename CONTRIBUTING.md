# Contributing to SIEM Dashboard

Thank you for considering contributing to the SIEM Dashboard project! This document provides guidelines for contributions.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Numbered steps to reproduce
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Docker version, ELK stack version
- **Logs**: Relevant log excerpts

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Use Case**: Why is this enhancement needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions considered
- **Additional Context**: Screenshots, examples, etc.

### Pull Requests

1. **Fork the Repository**
```bash
git clone https://github.com/yourusername/siem-dashboard.git
cd siem-dashboard
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**
   - Follow the coding standards
   - Add tests if applicable
   - Update documentation

3. **Test Your Changes**
```bash
# Run tests
python -m pytest tests/

# Test with Docker
docker-compose up -d
python scripts/setup_siem.py
python scripts/generate_test_logs.py
```

4. **Commit Your Changes**
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

Follow commit message convention:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements
- `Docs:` for documentation changes

5. **Push and Create PR**
```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub.

## Development Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use type hints where applicable
- Add docstrings to functions
- Maximum line length: 100 characters

**JavaScript/JSON:**
- Use 2-space indentation
- Follow standard linting rules
- Add comments for complex logic

### Detection Rules

When adding new detection rules:

1. Create JSON file in `detection-rules/`
2. Include all required fields:
   - rule_id
   - name
   - description
   - severity
   - query
   - threshold
   - mitre_attack
   - false_positives
   - investigation_guide
   - response_actions

3. Test the rule:
```bash
python scripts/test_detection_rules.py
```

4. Document the rule in `docs/DETECTION_RULES.md`

### Dashboard Contributions

1. Create dashboard in Kibana
2. Export as NDJSON
3. Save to `dashboards/` directory
4. Add description in README

### Documentation

- Update relevant documentation
- Add examples where applicable
- Keep README.md up to date
- Update CHANGELOG.md

## Testing

### Unit Tests

```bash
python -m pytest tests/ -v
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Run integration tests
python tests/integration_test.py
```

### Manual Testing Checklist

- [ ] Services start successfully
- [ ] Logs are ingested correctly
- [ ] Detection rules trigger appropriately
- [ ] Dashboards display correctly
- [ ] Alerts are sent
- [ ] Documentation is clear

## Project Structure

```
siem-dashboard/
├── config/              # Configuration files
├── dashboards/          # Kibana dashboards
├── detection-rules/     # Detection rule definitions
├── docs/               # Documentation
├── logstash/           # Logstash configuration
├── scripts/            # Helper scripts
└── tests/              # Test files
```

## Review Process

1. **Automated Checks**: GitHub Actions run tests
2. **Code Review**: Maintainers review code
3. **Testing**: Changes tested in test environment
4. **Merge**: After approval, PR is merged

## Community Guidelines

- Be respectful and inclusive
- Help others learn
- Provide constructive feedback
- Focus on the code, not the person

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

## Questions?

- Open a GitHub Discussion
- Check existing issues and PRs
- Review documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to making security monitoring more accessible!
