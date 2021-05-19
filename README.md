# sblgnt-tei
TEI XML transcriptions of the text and apparatus of the _SBL Greek New Testament_

## About This Project
While the Society of Biblical Literature and Logos Bible Software have generously made the _SBL Greek New Testament_ (SBLGNT) freely available in various formats at https://sblgnt.com/, at the time of this writing, most of these formats present the main text and textual apparatus of the edition in separate files, so that anyone who wants to convert the edition starting from one of these formats must do so separately for the text and apparatus or find some way to combine them in the conversion. In fact, this project arose as a stepping stone in my own effort to convert the SBLGNT to Unified Standard Format Markers (USFM) format.

In the interest of simplifying this process for others, I have modified the standard XML files for the SBLGNT to conform to the Text Encoding Initiative (TEI) standard (https://tei-c.org/). Specifically, I have used elements from the TEI's Critical Apparatus module (`<app/>`, `<lem/>`, `<rdg/>`) to encode the contents of the SBLGNT apparatus in line with the text.

Because a few textual variants in the SBLGNT overlap with verse boundaries, I had to decide on how to encode chapters, verses, apparatuses, and other textual divisions to respect XML's hierarchical structure. I have done this in two ways to assist researchers with different aims:
- A "simple" encoding is available in the `xml/sblgnt_tei.xml` file. In this encoding, chapter and verse divisions are marked by flat `<milestone/>` elements; if a textual variant overlaps with a chapter or verse boundary, then the associated `<milestone/>` element will occur within the `<lem/>` child of the `<app/>` element. Book titles are situated `<ab/>` (abstract textual block) elements within `<div/>`s with `type="incipit"`, and the text proper is organized in paragraphs under `<p/>` elements (textual variants do not overlap with paragraph breaks in the SBLGNT, so this is allowable).
- A stricter encoding based on the CapiTainS guidelines (http://capitains.org/pages/guidelines) is also available in the `xml/sblgnt_tei_capitains.xml` file. In this encoding, titles, chapters, and verses are rendered hierarchically as `<div/>`s of type `"incipit"`, `"chapter"`, or `"verse"`, and for each division, its text is rendered in an `<ab/>` element beneath it. Paragraphs in this encoding are rendered as flat `<lb/>` elements with `rend="indent"`. Finally, `<app/>` elements are rendered as usual, but those that would otherwise overlap a chapter or verse division have been divided and assigned `xml:id` and `prev` or `next` attributes to allow for the divided portions to be linked.

The SBLGNT is subject to the SBLGNT EULA, which can be found at http://sblgnt.com/license/ or in the `LICENSE` file in this repository.