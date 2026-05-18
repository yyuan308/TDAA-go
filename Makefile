.PHONY: all clean serve build pdfs viewers index setup-guide about instructor-guide student-guide styles assets compile-tests dump-solutions help watch serve-only

# Output directory
SITE_DIR := _site
PDF_DIR := $(SITE_DIR)/pdfs
ASSET_DIR := $(SITE_DIR)/assets
FIG_MAIN_SRC := .github/templates/assets/fig-main.svg

# Course metadata source — prefer config.toml, fall back to the example.
CFG_FILE := $(shell [ -f config.toml ] && echo config.toml || echo config.toml.example)
# Get raw value, then:
#   (a) HTML-escape & < > so angle-bracketed placeholders ("<Course Name>")
#       render literally on the page, and
#   (b) escape the resulting & as \& so it survives sed's special-char
#       handling when the value is interpolated into SUB_HTML below.
CFG_GET   = $(shell awk -F' *= *' '/^$(1)[[:space:]]*=/{sub(/^[ \t]*"/,"",$$2);sub(/"[ \t]*$$/,"",$$2);print $$2;exit}' $(CFG_FILE) | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/&/\\\&/g')

COURSE_CODE      := $(call CFG_GET,course-code)
COURSE_NAME      := $(call CFG_GET,course-name)
INSTITUTION      := $(call CFG_GET,institution)
TEXTBOOK_AUTHOR  := $(call CFG_GET,textbook-author)
TEXTBOOK_TITLE   := $(call CFG_GET,textbook-title)
TEXTBOOK_EDITION := $(call CFG_GET,textbook-edition)
TEXTBOOK_SHORT_RAW := $(call CFG_GET,textbook-short)
TEXTBOOK_SHORT   := $(if $(TEXTBOOK_SHORT_RAW),$(TEXTBOOK_SHORT_RAW),$(TEXTBOOK_AUTHOR))
# TEXTBOOK_INFO intentionally contains <em>; values inside are already escaped.
TEXTBOOK_INFO    := $(TEXTBOOK_AUTHOR), <em>$(TEXTBOOK_TITLE)</em> ($(TEXTBOOK_EDITION))

# Common sed substitutions for HTML site placeholders.
SUB_HTML = sed \
	-e 's|{{COURSE_CODE}}|$(COURSE_CODE)|g' \
	-e 's|{{COURSE_NAME}}|$(COURSE_NAME)|g' \
	-e 's|{{INSTITUTION}}|$(INSTITUTION)|g' \
	-e 's|{{TEXTBOOK_SHORT}}|$(TEXTBOOK_SHORT)|g' \
	-e 's|{{TEXTBOOK_INFO}}|$(TEXTBOOK_INFO)|g'

# Find all *.learning-sheet.typ files (exclude templates/)
LEARNING_SHEETS := $(shell find . -path ./templates -prune -o -name "*learning-sheet.typ" -print | sort -V)

# Find test.typ, test.B.typ, validation.typ files (exclude templates/)
TEST_FILES := $(shell find . -path ./templates -prune -o \( -name "*.test.typ" -o -name "*.test.B.typ" \) -print | sort -V)
VALIDATION_FILES := $(shell find . -path ./templates -prune -o -name "*.validation.typ" -print | sort -V)

all: build

build: pdfs viewers setup-guide about instructor-guide student-guide index
	@echo "✅ Build complete! Run 'make serve' to preview locally."

# Create directories
$(SITE_DIR):
	mkdir -p $(SITE_DIR)

$(PDF_DIR): $(SITE_DIR)
	mkdir -p $(PDF_DIR)

$(ASSET_DIR): $(SITE_DIR)
	mkdir -p $(ASSET_DIR)

# Compile learning sheets to PDFs
pdfs: $(PDF_DIR)
	@echo "📄 Compiling learning sheets to PDF..."
	@for file in $(LEARNING_SHEETS); do \
		dir=$$(dirname "$$file"); \
		basename=$$(basename "$$file" .typ); \
		week=$$(basename "$$dir"); \
		echo "  → $$file"; \
		typst compile --root . "$$file" "$(PDF_DIR)/$${week}-$${basename}.pdf"; \
	done

# Compile all test and validation files to PDFs
compile-tests: $(PDF_DIR)
	@echo "📝 Compiling test and validation files to PDF..."
	@for file in $(TEST_FILES); do \
		dir=$$(dirname "$$file"); \
		basename=$$(basename "$$file" .typ); \
		week=$$(basename "$$dir"); \
		echo "  → $$file"; \
		typst compile --root . "$$file" "$(PDF_DIR)/$${week}-$${basename}.pdf"; \
	done
	@for file in $(VALIDATION_FILES); do \
		dir=$$(dirname "$$file"); \
		basename=$$(basename "$$file" .typ); \
		week=$$(basename "$$dir"); \
		echo "  → $$file"; \
		typst compile --root . "$$file" "$(PDF_DIR)/$${week}-$${basename}.pdf"; \
	done
	@echo "✅ Test and validation PDFs compiled to $(PDF_DIR)/"

# Compile all test and validation files with solutions visible
dump-solutions: $(PDF_DIR)
	@echo "📝 Compiling test and validation files with solutions..."
	@for file in $(TEST_FILES); do \
		dir=$$(dirname "$$file"); \
		basename=$$(basename "$$file" .typ); \
		week=$$(basename "$$dir"); \
		echo "  → $$file"; \
		typst compile --root . --input hide-solution=false "$$file" "$(PDF_DIR)/$${week}-$${basename}-solution.pdf"; \
	done
	@for file in $(VALIDATION_FILES); do \
		dir=$$(dirname "$$file"); \
		basename=$$(basename "$$file" .typ); \
		week=$$(basename "$$dir"); \
		echo "  → $$file"; \
		typst compile --root . --input hide-solution=false "$$file" "$(PDF_DIR)/$${week}-$${basename}-solution.pdf"; \
	done
	@echo "✅ Solution PDFs compiled to $(PDF_DIR)/"

# Generate PDF viewer pages
viewers: pdfs
	@echo "🖼️  Generating PDF viewer pages..."
	@for pdf in $(PDF_DIR)/*.pdf; do \
		[ -f "$$pdf" ] || continue; \
		filename=$$(basename "$$pdf" .pdf); \
		weekNum=$$(echo "$$filename" | grep -oE 'week[0-9]+' | sed 's/week//'); \
		week="Week $${weekNum}"; \
		typfile=$$(find . -path "./week$${weekNum}/*learning-sheet.typ" 2>/dev/null | head -1); \
		if [ -n "$$typfile" ]; then \
			title=$$(grep -oP '#set document\(title: "\K[^"]+' "$$typfile" 2>/dev/null | sed "s/Week $${weekNum} - //"); \
		else \
			title="Learning Sheet"; \
		fi; \
		[ -z "$$title" ] && title="Learning Sheet"; \
		escaped_title=$$(echo "$$title" | sed 's/\&/\\\\\\&/g'); \
		$(SUB_HTML) .github/templates/viewer.html | \
		awk -v week="$$week" -v title="$$escaped_title" -v fname="$$filename" \
			'{gsub(/\{\{WEEK\}\}/, week); gsub(/\{\{TITLE\}\}/, title); gsub(/\{\{FILENAME\}\}/, fname); print}' \
			> "$(SITE_DIR)/$${filename}.html" 2>/dev/null; \
	done

# Copy CSS styles
styles: $(SITE_DIR)
	@echo "🎨 Copying styles..."
	cp .github/templates/styles.css $(SITE_DIR)/styles.css

# Copy static page assets
assets: $(ASSET_DIR) $(FIG_MAIN_SRC)
	@echo "🖼️  Copying static assets..."
	cp $(FIG_MAIN_SRC) $(SITE_DIR)/assets/fig-main.svg

# Render setup guide (substitute course placeholders from config.toml)
setup-guide: $(SITE_DIR) styles
	@echo "📚 Rendering setup guide..."
	@$(SUB_HTML) .github/templates/setup-guide.html > $(SITE_DIR)/setup-guide.html

# Render About TDAA page
about: $(SITE_DIR) styles assets
	@echo "📖 Rendering About TDAA page..."
	@$(SUB_HTML) .github/templates/about.html > $(SITE_DIR)/about.html

# Render instructor's guide page (linked from About, not in main nav)
instructor-guide: $(SITE_DIR) styles
	@echo "🧑‍🏫 Rendering instructor's guide..."
	@$(SUB_HTML) .github/templates/instructor-guide.html > $(SITE_DIR)/instructor-guide.html

# Render student guide page
student-guide: $(SITE_DIR) styles
	@echo "🎓 Rendering student guide..."
	@$(SUB_HTML) .github/templates/student-guide.html > $(SITE_DIR)/student-guide.html

# Generate index page
index: viewers setup-guide about instructor-guide student-guide styles
	@echo "🏠 Generating index page..."
	@pages="["; \
	first=true; \
	for file in $$(ls $(SITE_DIR)/*.html 2>/dev/null | grep -v index.html | grep -v setup-guide.html | grep -v about.html | grep -v instructor-guide.html | grep -v student-guide.html | sort -V); do \
		filename=$$(basename "$$file"); \
		weekNum=$$(echo "$$filename" | grep -oE 'week[0-9]+' | sed 's/week//'); \
		week="Week $${weekNum}"; \
		typfile=$$(find . -path "./week$${weekNum}/*learning-sheet.typ" 2>/dev/null | head -1); \
		if [ -n "$$typfile" ]; then \
			title=$$(grep -oP '#set document\(title: "\K[^"]+' "$$typfile" 2>/dev/null || echo ""); \
		else \
			title=""; \
		fi; \
		if [ "$$first" = true ]; then \
			first=false; \
		else \
			pages="$$pages,"; \
		fi; \
		escaped_title=$$(echo "$$title" | sed 's/"/\\"/g'); \
		pages="$$pages{\"file\":\"$$filename\",\"week\":\"$$week\",\"weekNum\":\"$${weekNum}\",\"title\":\"$${escaped_title}\"}"; \
	done; \
	pages="$$pages]"; \
	escaped_pages=$$(echo "$$pages" | sed 's/&/\\\\\\&/g'); \
	$(SUB_HTML) .github/templates/index.html | \
	awk -v pages="$$escaped_pages" '{gsub(/\{\{PAGES_JSON\}\}/, pages); print}' 2>/dev/null > $(SITE_DIR)/index.html

# Serve locally
serve: build
	@echo "🌐 Starting local server at http://localhost:8000"
	@echo "   Press Ctrl+C to stop"
	@cd $(SITE_DIR) && python3 -m http.server 8000

# Alternative: serve without rebuilding
serve-only:
	@echo "🌐 Starting local server at http://localhost:8000"
	@echo "   Press Ctrl+C to stop"
	@cd $(SITE_DIR) && python3 -m http.server 8000

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf $(SITE_DIR)

# Watch for changes and rebuild (requires entr)
watch:
	@echo "👀 Watching for changes... (requires 'entr' to be installed)"
	@while true; do \
		find . -name "*.typ" -o -name "*.html" | grep -v $(SITE_DIR) | entr -d $(MAKE) build; \
	done

help:
	@echo "Course Materials - Local Development"
	@echo ""
	@echo "Usage:"
	@echo "  make build          Build the site (PDFs + viewer pages)"
	@echo "  make serve          Build then serve at http://localhost:8000"
	@echo "  make serve-only     Serve without rebuilding"
	@echo "  make compile-tests  Compile all test.typ and validation.typ to PDF"
	@echo "  make dump-solutions Compile tests and validations with solutions visible"
	@echo "  make clean          Remove build artifacts"
	@echo "  make watch          Watch for changes and rebuild (requires entr)"
	@echo ""
	@echo "Requirements: typst, python3 (entr optional for watch mode)"
