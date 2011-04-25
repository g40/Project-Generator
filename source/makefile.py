import project_writer
import os
import project_path
import re

class Makefile:
	def __init__(self, project, source_root, platform):
		self.output = None
		self.project = project
		self.source_root = source_root

	def output_variable(self, variable, content):
		self.output.output(variable + " = " + content)
		self.output.output("")

	def output_variable_list(self, variable, contents):
		s = ""
		for content in contents:
			s = s + " " + content

		self.output_variable(variable, s)

	def output_target_dependency(self, target, dependency):
		self.output.output(target + ": " + dependency)
		self.output.increase_tabs()

	def output_target_dependencies(self, target, dependencies, commands):
		self.output.output("")
		s = ""
		for dependency in dependencies:
			s = s + " " + dependency
		
		self.output_target_dependency(target, s)
		for command in commands:
			self.output_command(command)
		self.output.decrease_tabs()

	def output_command(self, command):
		self.output.output(command)
	
	def change_extension(self, filename, new_extension):
		return file_without_extension + "." + new_extension

	def write(self, output):
		self.output = output
	
		complete_sources = self.project.source_filenames()
		objects = []
		sources = []

		for source in complete_sources:
			path = project_path.Path(source)
			relative_source = path.relative(self.source_root)
			file_without_extension, extension = os.path.splitext(relative_source)
			if extension == ".cpp" or extension == ".c":
				sources.append(relative_source)
				objects.append(file_without_extension + ".o")


		includes = self.project.include_paths()
		include_string = " -I" + " -I".join(includes)
	
		self.output_variable_list("cc", ["g++"])
		self.output_variable_list("c", ["g++", "-x c", "-std=c99"])
		self.output_variable_list("cflags", ["-c", "-Wall", include_string])
		self.output_variable_list("ldflags", [])

		self.output_variable_list("sources", sources)
		self.output_variable_list("objects", objects)
		self.output_variable_list("executable", [self.project.target_name + ".out"])

		self.output_target_dependencies("all", [self.project.target_name], [])
		self.output_target_dependencies("clean", "", ["@rm -f $(objects)", "@echo clean done!"])
		self.output_target_dependencies(self.project.target_name, ["$(sources) $(executable)"], ["echo $<"])
		self.output_target_dependencies("$(executable)", ["$(objects)"], ["@echo linking $@", "@$(cc) $(ldflags) $(objects) -o $@"])
		self.output_target_dependencies(".c.o", [], ["@$(c) $(cflags) $< -o $@"])
		self.output_target_dependencies(".cpp.o", [], ["@$(cc) $(cflags) $< -o $@"])
		self.output_target_dependencies("depend", [], ["makedepend -f " + self.output.target_path + "Makefile -- $(cflags) -- $(sources) -I" + include_string])

	def close(self, output):
		self.output.output("# DO NOT DELETE")
		pass

	def change_short_name_for_file_references(self, output):
		pass