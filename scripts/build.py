"""One command to regenerate the website and every language's CV."""
import argparse
from content import LANGUAGES, validate
from build_site import build as build_site


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-only',action='store_true',help='Skip PDF generation for changes that only affect the website.')
    args=parser.parse_args()
    validate()
    if not args.site_only:
        from build_cv import build as build_cv, configure_fonts
        configure_fonts()
    build_site()
    if not args.site_only:
        for lang in LANGUAGES:
            build_cv(lang)


if __name__=='__main__':
    main()
