# Excluding Content (Headers/Footers)

Often, PDFs have repeating headers or footers on every page that you want to ignore when extracting the main content. `natural-pdf` allows you to define exclusion regions.

We'll use a different PDF for this example, which has a distinct header and footer section: `0500000US42007.pdf`.

```python
#%pip install natural-pdf
```


```python
from natural_pdf import PDF

pdf_url = "https://github.com/jsoma/natural-pdf/raw/refs/heads/main/pdfs/0500000US42007.pdf"

# Load the PDF
pdf = PDF(pdf_url)
page = pdf.pages[0]

# Let's see the bottom part of the text WITHOUT exclusions
# It likely contains page numbers or other footer info.
full_text_unfiltered = page.extract_text()

# Show the last 200 characters (likely containing footer text)
full_text_unfiltered[-200:]
```

## Approach 1: Excluding a Fixed Area

A simple way to exclude headers or footers is to define a fixed region based on page coordinates. Let's exclude the bottom 200 pixels of the page.

```python
from natural_pdf import PDF

pdf_url = "https://github.com/jsoma/natural-pdf/raw/refs/heads/main/pdfs/0500000US42007.pdf"
pdf = PDF(pdf_url)

# Define the exclusion region on every page using a lambda function
footer_height = 200
pdf.add_exclusion(
    lambda page: page.region(top=page.height - footer_height),
    label="Bottom 200pt Footer"
)

# Now extract text from the first page again, exclusions are active by default
page = pdf.pages[0]

# Visualize the excluded area
footer_region_viz = page.region(top=page.height - footer_height)
footer_region_viz.show(label="Excluded Footer Area")
page.show()
```

```python
filtered_text = page.extract_text() # use_exclusions=True is default

# Show the last 200 chars with footer area excluded
filtered_text[-200:]
```

This method is simple but might cut off content if the footer height varies or content extends lower on some pages.

## Approach 2: Excluding Based on Elements

A more robust way is to find specific elements that reliably mark the start of the footer (or end of the header) and exclude everything below (or above) them. In `Examples.md`, the footer was defined as everything below the last horizontal line.

### Smart Exclusion Behavior

Natural PDF uses intelligent exclusion logic depending on what you're excluding:

- **Text elements**: When you exclude a text element directly, only that specific text is excluded from extraction
- **Regions**: When you exclude a region (created with `.below()`, `.above()`, etc.), everything within that region is excluded

This allows for precise control - you can exclude just specific text elements (like page numbers) or entire areas (like footer regions).

```python
from natural_pdf import PDF

pdf_url = "https://github.com/jsoma/natural-pdf/raw/refs/heads/main/pdfs/0500000US42007.pdf"
pdf = PDF(pdf_url)
page = pdf.pages[0] # Get page for finding elements

# Find the last horizontal line on the first page
# We'll use this logic to define our exclusion for all pages
last_line = page.find_all('line')[-1]

# Define the exclusion function using a lambda
# This finds the last line on *each* page and excludes below it
pdf.add_exclusion(
    lambda p: p.find_all('line')[-1].below(),
    label="Element-Based Footer"
)

# Extract text again, with the element-based exclusion active
filtered_text_element = page.extract_text()

# Show the last 200 chars with element-based footer exclusion
"Element-Based Excluded (last 200 chars): " + filtered_text_element[-200:]

# Visualize the element-based exclusion area
page.clear_highlights()
# Need to find the region again for visualization
footer_boundary = page.find_all('line')[-1]
footer_region_element = footer_boundary.below()
footer_region_element.show(label="Excluded Footer Area (Element)")
page.show()
```

This element-based approach is usually more reliable as it adapts to the content's position, but it depends on finding consistent boundary elements (like lines or specific text markers).

## Approach 3: Excluding Specific Text Elements

Sometimes you want to exclude only specific text elements (like page numbers) without excluding the entire surrounding area. Natural PDF's smart exclusion logic makes this easy.

```python
# Exclude only the page number text itself
pdf.add_exclusion(
    lambda p: p.find('text:contains("Page ")'),
    label="Page numbers only"
)

# This excludes ONLY the "Page X" text, not the entire footer area
filtered_text = page.extract_text()
```

Compare this with region-based exclusion:

```python
# Exclude the entire area below the page number
pdf.add_exclusion(
    lambda p: p.find('text:contains("Page ")').below(),
    label="Everything below page numbers"
)

# This excludes the page number AND everything below it
```

## Working with Multiple Exclusions

You can stack multiple exclusions - they are applied in the order they were added:

```python
# Add header exclusion
pdf.add_exclusion(
    lambda p: p.region(bottom=100),  # Top 100px
    label="Header"
)

# Add footer exclusion
pdf.add_exclusion(
    lambda p: p.find_all('line')[-1].below() if p.find_all('line') else None,
    label="Footer"
)

# Add specific text exclusion
pdf.add_exclusion(
    lambda p: p.find_all('text:contains("CONFIDENTIAL")'),
    label="Confidential markers"
)
```

## Enhanced Exclusion Support

Exclusions now support returning collections of elements:

```python
# Exclude all headers on the page
pdf.add_exclusion(
    lambda page: page.find_all('text:contains("Header")'),
    label="All headers"
)

# Exclude multiple specific elements
pdf.add_exclusion(
    lambda page: [
        page.find('text:contains("Draft")'),
        page.find('text:contains("Confidential")'),
        page.find_all('text[color=red]')  # Returns ElementCollection
    ],
    label="Multiple exclusions"
)
```

## Temporarily Disabling Exclusions

You can disable exclusions for specific operations:

```python
# Extract with exclusions (default)
filtered_text = page.extract_text()  # use_exclusions=True by default

# Extract without exclusions
full_text = page.extract_text(use_exclusions=False)

print(f"With exclusions: {len(filtered_text)} chars")
print(f"Without exclusions: {len(full_text)} chars")
```

<div class="admonition note">
<p class="admonition-title">Applying Exclusions</p>

    *   `pdf.add_exclusion(func)` applies the exclusion function to *all* pages in the PDF
    *   `page.add_exclusion(region)` adds an exclusion only to that specific page
    *   Exclusion functions can return:
        - A single `Region` to exclude an area
        - A single `Element` to exclude just that element
        - An `ElementCollection` or list/iterable of elements
        - `None` to exclude nothing on that page
    *   `extract_text(use_exclusions=False)` temporarily disables exclusions
    *   Smart exclusion: text elements exclude only themselves, regions exclude everything inside
</div>
