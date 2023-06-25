import click

class NestedGroup(click.Group):
  def format_commands(self, ctx, formatter):
    def get_section_dfs(group: NestedGroup, ctx: click.Context):
      section = {'section': (group.name, group.help), 'commands': []}

      names = group.list_commands(ctx)
      for name in names:
        command = group.get_command(ctx, name)
        if command is None:
          continue

        if isinstance(command, NestedGroup):
          section['commands'].append(get_section_dfs(command, ctx))
        else:
          section['commands'].append({'command': (name, command.help or "")})

      return section

    def update_command_names_dfs(name: str, section: dict):
      for command in section['commands']:
        if 'section' in command:
          update_command_names_dfs(f"{name} {command['section'][0]}", command)
        else:
          command_name, help_message = command['command']
          command['command'] = (f"{name} {command_name}", help_message)

    def get_help_messages_dfs(section: dict):
      messages = []
      for command in section['commands']:
        if 'section' in command:
          messages.extend(get_help_messages_dfs(command))
        else:
          messages.append(command['command'])
      return messages

    sections = get_section_dfs(self, ctx)
    update_command_names_dfs("", sections)

    commands = []
    commands.extend([
      command['command']
      for command in sections['commands']
      if 'command' in command
    ])
    commands.extend([
      command['section']
      for command in sections['commands']
      if 'section' in command
    ])

    if commands:
      with formatter.section("main commands"):
        formatter.write_dl(commands)

    section_names = [
      command['section'][0]
      for command in sections['commands']
      if 'section' in command
    ]
    for section_name in section_names:
      section = [
        command
        for command in sections['commands']
        if 'section' in command
        and command['section'][0] == section_name
      ][0]
      with formatter.section(f"{section_name} commands"):
        formatter.write_dl(get_help_messages_dfs(section))

class RuntimeStub:
  # only symbole definition is needed
  pass

runtime = click.make_pass_decorator(RuntimeStub, ensure=True)
@click.group(cls=NestedGroup)
@runtime
@click.pass_context
def cli(ctx: click.Context, _):
  ctx.obj = Runtime()

class Runtime(RuntimeStub):
  @cli.group(help='App commands', cls=NestedGroup)
  @runtime
  def app():
    pass

  @app.command(help='Build an app')
  @runtime
  @click.argument('name')
  def build(name):
    click.echo(f"Building app: {name}")

  @app.command(help='Test an app')
  @runtime
  @click.argument('name')
  def test(name):
    click.echo(f"Testing app: {name}")

  @app.group(help='Inspect commands', cls=NestedGroup)
  @runtime
  def inspect():
    pass

  @inspect.command(help='Get app name')
  @runtime
  def name():
    click.echo("name is app-something")

  @inspect.command(help='Get app version')
  @runtime
  def version():
    click.echo("version is x.y.z")

  @cli.group(help='Image commands', cls=NestedGroup)
  @runtime
  def image():
    pass

  @image.command(help='Build an image')
  @runtime
  @click.argument('name')
  def build(name):
    click.echo(f"Building image: {name}")

  @image.command(help='Push an image')
  @runtime
  @click.argument('name')
  def push(name):
    click.echo(f"Pushing image: {name}")

  @cli.group(help='Cluster commands', cls=NestedGroup)
  @runtime
  def cluster():
    pass

  @cluster.command(help='Load a cluster')
  @runtime
  @click.argument('name')
  def load(name):
    click.echo(f"Loading cluster: {name}")

  @cluster.command(help='Test a cluster')
  @runtime
  @click.argument('name')
  def test(name):
    click.echo(f"Testing cluster: {name}")

  @cluster.command(help='Clean a cluster')
  @runtime
  @click.argument('name')
  def clean(name):
    click.echo(f"Cleaning cluster: {name}")

if __name__ == '__main__':
  cli()
