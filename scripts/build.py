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
    from build_documents import build as build_documents
    build_documents()
    if not args.site_only:
        for lang in LANGUAGES:
            if lang == 'ko':
                # Reviewed Korean CV is maintained as an independent publication.
                # Do not overwrite it with the archived four-page editorial build.
                continue
            else:
                build_cv(lang)


if __name__=='__main__':
    main()


