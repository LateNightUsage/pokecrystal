crystal := ../

crystal_obj := $(shell find "$(crystal)/build/crystal" -name "*.o")

.PHONY: all
all: groups.txt

.PHONY: clean
clean:
	rm -rf __pycache__ groups.txt groups.merged.json groups.merged.raw.json groups.json groups.raw.json groups.test.json references.json references.raw.json bankless.json

.PHONY: test
test: test-groups test-crossbank test-crossbank-groups test-continuity test-equality

.PHONY: test-groups
test-groups: groups.raw.json groups.test.json
	cmp $^

.PHONY: test-crossbank
test-crossbank: test_crossbank.py $(crystal)/pokecrystal.sym references.json
	./$< -s $(filter-out $<, $^)

.PHONY: test-crossbank-groups
test-crossbank-groups: test_crossbank_groups.py $(crystal)/pokecrystal.sym groups.merged.json
	./$< -s $(filter-out $<, $^)

.PHONY: test-continuity
test-continuity: test_continuity.py $(crystal)/pokecrystal.sym groups.merged.json
	./$< -s $(filter-out $<, $^)

.PHONY: test-equality
test-equality: test_equality.py $(crystal)/pokecrystal.sym $(crystal)/pokecrystal.map groups.merged.json
	./$< -s $(crystal)/pokecrystal.sym -m $(crystal)/pokecrystal.map groups.merged.json

groups.txt: stats.py $(crystal)/pokecrystal.sym groups.merged.json
	./$< -o $@ -s $(filter-out $<, $^)

groups.merged.json: fix_mergegroups.py references.json groups.merged.raw.json
	./$< -o $@ -p "$(crystal)" -r $(filter-out $<, $^)

groups.merged.raw.json: mergegroups.py $(crystal)/pokecrystal.sym groups.json
	./$< -o $@ -s $(filter-out $<, $^)

groups.json: fix_groups.py $(crystal)/pokecrystal.sym groups.raw.json
	./$< -p "$(crystal)" groups.raw.json $@

groups.raw.json groups.test.json: %: makegroups.py references.json bankless.json
	./$< -o $@ $(filter-out $<, $^)

references.json: fix_references.py $(crystal)/pokecrystal.sym references.raw.json
	./$< -p "$(crystal)" references.raw.json $@

bankless.json: references.raw.json
references.raw.json: references.py $(crystal_obj)
	./$< -o $@ -b bankless.json -p "$(crystal)" $(filter-out $<, $^)
