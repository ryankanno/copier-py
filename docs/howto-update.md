# How to Update an Existing Project

This guide covers updating a project that was generated with copier-py to incorporate template improvements.

## Update to the latest template

Run `copier update` in your project directory:

```sh
cd /path/to/your-project
copier update --trust
```

Copier compares your project against the latest template version and applies changes. If there are conflicts between your modifications and template updates, copier presents a diff for you to resolve.

## Update to a specific template version

To update to a specific tag or commit of the template:

```sh
copier update --trust --vcs-ref v1.2.0
```

## Change configuration options

To change options you selected during initial generation (e.g., enable publishing, change the Sphinx theme):

```sh
copier update --trust
```

Copier re-prompts you for all configuration values, pre-filled with your previous answers. Change any values you want and copier regenerates the affected files.

## Review changes before applying

To see what would change without applying:

```sh
copier update --trust --pretend
```

This performs a dry run and shows the diff.

## Resolve conflicts

When copier detects conflicts between your changes and template updates:

1. Copier creates `.rej` files containing the rejected hunks
2. Review each `.rej` file and manually apply the intended changes
3. Delete the `.rej` files after resolving

Search for rejection files:

```sh
find . -name "*.rej"
```

## Skip specific questions

If you want to keep specific answers unchanged and skip their prompts:

```sh
copier update --trust --defaults
```

This uses your previously saved answers (stored in `.copier-answers.yml`) without prompting.
