#!/bin/bash
resume_path="$1"
json_file_name="$2"
echo "$resume_path"
echo "$json_file_name"

cd ..
cd ResumeParser/ResumeTransducer/
java -cp 'bin/*:../GATEFiles/lib/*:../GATEFiles/bin/gate.jar:lib/*' code4goal.antony.resumeparser.ResumeParserProgram "$resume_path" "$json_file_name"
