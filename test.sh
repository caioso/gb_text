array=(`find ./tests -type f -name "*.py"`)

for test in ${array[@]}
do
  if [[ "${test}" == *"__init__.py"* || "${test}" == *"test_case.py"* ]]; then
    continue
  fi

  # Run test
  python3 ${test} /Users/caiooliveira/Projects/gb/gb-hello-world/test
  [ $? -ne 0 ] && echo "Aborting test" && exit 1
done