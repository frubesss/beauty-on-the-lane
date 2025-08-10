# Beauty on the Lane - GitHub Copilot Instructions

**ALWAYS follow these instructions first and only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in error.**

Beauty on the Lane is a static HTML website for a beauty salon in Bromborough, Wirral. The site is deployed via GitHub Pages with no build process required.

## Working Effectively

### Bootstrap and Test the Repository
- Clone the repository: `git clone https://github.com/frubesss/beauty-on-the-lane.git`
- Navigate to repository: `cd beauty-on-the-lane`
- No installation steps required - this is a static HTML website with no dependencies

### Running the Website Locally
- Start local HTTP server: `python3 -m http.server 8000`
- Access website at: `http://localhost:8000`
- Stop server with: `Ctrl+C`
- **TIMING**: Server starts immediately (< 5 seconds)

### Validation Commands
- Validate HTML syntax: 
```bash
python3 -c "
import html.parser
import sys

class HTMLValidator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []
    
    def error(self, message):
        self.errors.append(message)

try:
    with open('index.html', 'r') as f:
        content = f.read()
    
    validator = HTMLValidator()
    validator.feed(content)
    
    if validator.errors:
        print('HTML validation errors found:')
        for error in validator.errors:
            print(f'  - {error}')
        sys.exit(1)
    else:
        print('HTML is well-formed')
except Exception as e:
    print(f'Error validating HTML: {e}')
    sys.exit(1)
"
```
- **TIMING**: HTML validation completes in < 2 seconds

### Testing HTTP Responses
- Test main page loads: `curl -s -I http://localhost:8000/`
- Test HTML content: `curl -s http://localhost:8000/ | head -20`
- Test favicon: `curl -s -I http://localhost:8000/favicon.ico`
- Test logo: `curl -s -I http://localhost:8000/images/logo.svg`
- **TIMING**: Each HTTP test completes in < 1 second

### Git Operations
- Check repository status: `git --no-pager status`
- View recent changes: `git --no-pager diff`
- View commit history: `git --no-pager log --oneline -10`
- **TIMING**: Git commands complete in < 5 seconds

## Manual Validation Requirements

**CRITICAL**: After making any changes, you MUST perform complete manual validation by running through these scenarios:

### Scenario 1: Website Loading and Navigation
1. Start local server: `python3 -m http.server 8000`
2. Open browser or use curl to test: `curl -s http://localhost:8000/`
3. Verify HTML loads completely (should return 200 OK)
4. Test all static assets load: 
   - `curl -s -I http://localhost:8000/favicon.ico` (should return 200 OK)
   - `curl -s -I http://localhost:8000/images/logo.svg` (should return 200 OK)
   - `curl -s -I http://localhost:8000/images/favicon.svg` (should return 200 OK)

### Scenario 2: Content Validation
1. Validate HTML structure is well-formed using the Python validation script above
2. Check that all prices are in British Pounds (£) format
3. Verify business information is accurate:
   - Address: 8 Allport Lane, Bromborough, Wirral, CH62 7HP
   - Phone: +441513430877
   - Domain: beautyonthelane-wirral.co.uk

### Scenario 3: SEO and Metadata Validation
1. Check meta tags are present: `curl -s http://localhost:8000/ | grep -i "meta name="`
2. Verify structured data: `curl -s http://localhost:8000/ | grep -A 20 "application/ld+json"`
3. Confirm Open Graph tags: `curl -s http://localhost:8000/ | grep "og:"`

## Common Tasks

### Updating Treatment Prices
- Edit `index.html` directly
- Locate the relevant `<table>` section
- Update prices in `<td>` elements using £XX format
- Always run validation scenario after changes

### Adding New Treatments
- Add new `<tr>` elements to appropriate treatment tables in `index.html`
- Include: Treatment name, Duration (if applicable), Price in £XX format
- Maintain consistent table structure
- Run complete validation after changes

### Modifying Business Information
- Update contact details in the `<header>` section of `index.html`
- Update Schema.org structured data in `<script type="application/ld+json">` section
- Update meta tags if business description changes
- Ensure consistency across all locations

### Adding Images
- Add images to `/images/` directory
- Use descriptive filenames
- Reference in HTML with proper `alt` attributes
- Test image loading with: `curl -s -I http://localhost:8000/images/[filename]`

## Repository Structure

### Key Files and Directories
```
/home/runner/work/beauty-on-the-lane/beauty-on-the-lane/
├── .git/                    # Git repository data
├── .github/                 # GitHub configuration (this file)
├── images/                  # Static assets
│   ├── favicon.svg         # Site favicon
│   └── logo.svg            # Site logo
├── .copilot-instructions.md # Detailed project documentation
├── .gitignore              # Git ignore rules
├── CNAME                   # GitHub Pages domain configuration
├── favicon.ico             # Site favicon (ICO format)
└── index.html              # Main website file (347 lines)
```

### File Sizes and Expectations
- `index.html`: ~15KB, 347 lines
- `images/logo.svg`: ~440 bytes
- `images/favicon.svg`: Small SVG file
- `favicon.ico`: 280 bytes

## Deployment

### GitHub Pages Configuration
- **Source**: Repository root (main branch)
- **Custom Domain**: beautyonthelane-wirral.co.uk (configured via CNAME file)
- **HTTPS**: Automatically enabled by GitHub Pages
- **Deployment**: Automatic on push to main branch
- **TIMING**: Deployment typically takes 2-5 minutes after push

### Domain Management
- Domain DNS points to GitHub Pages
- CNAME file contains: `beautyonthelane-wirral.co.uk`
- Any domain changes require updating both DNS and CNAME file

## Build and Test Expectations

### No Build Process
- **CRITICAL**: This is a static HTML website with NO build process
- Do not attempt to run `npm install`, `npm run build`, or similar commands
- Do not look for package.json, Makefile, or other build configuration files
- Changes to HTML/CSS are immediately effective

### Testing Requirements
- **Local Testing**: ALWAYS test locally using `python3 -m http.server 8000`
- **Validation**: ALWAYS run HTML validation script after changes
- **Asset Testing**: ALWAYS verify all referenced assets load correctly
- **No Unit Tests**: This project has no automated test suite

### Timing Expectations
- Local server startup: < 5 seconds
- HTML validation: < 2 seconds  
- HTTP response tests: < 1 second each
- Git operations: < 5 seconds
- GitHub Pages deployment: 2-5 minutes

## Validation Checklist

Before completing any changes, verify:
- [ ] HTML validates with no errors using the Python validation script
- [ ] Local HTTP server serves the site correctly at `http://localhost:8000`
- [ ] All referenced assets return 200 OK status codes
- [ ] Business information remains accurate and consistent
- [ ] Prices are in proper £XX format
- [ ] Meta tags and structured data are intact
- [ ] Changes maintain the single-file HTML architecture

## Common Debugging

### Website Not Loading
- Ensure you're in the correct directory: `/home/runner/work/beauty-on-the-lane/beauty-on-the-lane`
- Check Python HTTP server is running: `python3 -m http.server 8000`
- Verify no other process is using port 8000: `lsof -i :8000`

### HTML Validation Errors
- Check for unclosed tags, invalid nesting, or syntax errors
- Ensure proper encoding (UTF-8) is maintained
- Verify all entities are properly escaped (&amp; for &, etc.)

### Asset Loading Issues  
- Verify file exists in correct location: `ls -la images/`
- Check file permissions: `ls -la images/[filename]`
- Test direct asset URL: `curl -s -I http://localhost:8000/images/[filename]`

### GitHub Pages Deployment Issues
- Verify CNAME file contains correct domain
- Check that main branch is set as Pages source
- Allow 5-10 minutes for DNS propagation after domain changes

## Additional Context

This is a professional beauty salon website serving the Bromborough, Wirral area. All changes should maintain:
- Professional, welcoming tone
- British English spelling and terminology  
- Accurate business information
- Clean, minimal design aesthetic
- Mobile-responsive layout
- SEO optimization

Always test changes locally before pushing to ensure deployment success.