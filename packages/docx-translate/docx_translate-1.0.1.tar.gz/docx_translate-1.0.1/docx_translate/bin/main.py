import time

import click
import loguru

from docx_translate import version_info
from docx_translate.core.translate import DocxTranslator


CONTEXT_SETTINGS = dict(help_option_names=['-?', '-h', '--help'])

epilog = click.style('''
\n\b
example:
    {prog} input.docx -o output.docx
    {prog} input.docx -o output.docx -t zh-CN
                     
contact: {author}<{author_email}>                   
''', fg='yellow').format(**version_info)

@click.command(
    name=version_info['prog'],
    help=click.style(version_info['desc'], italic=True, fg='cyan', bold=True),
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
    epilog=epilog,
)
@click.version_option(version=version_info['version'], prog_name=version_info['prog'])
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), help='output file', default='output.docx', show_default=True)
@click.option('-t', '--target', help='target language', default='en', show_default=True)
def cli(input_file, output, target):
    start_time = time.time()
    trans = DocxTranslator(target=target)
    trans.translate_docx(input_file, output)
    loguru.logger.info(f'time elapsed: {time.time() - start_time:.2f}s')


def main():
    cli()


if __name__ == '__main__':
    main()
