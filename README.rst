~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Advanzia plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project provides an ofxstatement plugin to import German Advanzia statements (Schmetterling Mastercard).

`ofxstatement`_ is a tool to convert proprietary bank statement to OFX format,
suitable for importing to GnuCash. Plugin for ofxstatement parses a
particular proprietary bank statement format and produces common data
structure, that is then formatted into an OFX file.

.. _ofxstatement: https://github.com/kedder/ofxstatement

The plugin has been tested against files named ``Rechnung_DD.MM.YYYY_***********.pdf``.
So far it only works for single-page PDFs. This will be fixed in a few weeks.
