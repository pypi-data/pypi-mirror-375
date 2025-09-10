#
#  InSillyClo
#  Copyright (C) 2025  The InSillyClo Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#


class InSillyCloFailureException(Exception):
    pass


class MissingInputPart(InSillyCloFailureException):
    pass


class InvalidePartTypesException(InSillyCloFailureException):
    pass


class InvalidePartTypesExpression(InvalidePartTypesException):
    pass


class InvalidePartTypesSeparator(InvalidePartTypesException):
    pass


class MissingSeparatorInPartTypesDeclaration(InvalidePartTypesException):
    pass


class InvalidePartFileHeader(InSillyCloFailureException):
    pass


class PrimerRelatedException(InSillyCloFailureException):
    pass


class InvalidePrimerFile(PrimerRelatedException):
    pass


class PrimerNotFound(PrimerRelatedException):
    pass


class MissingSequenceForInputPart(InSillyCloFailureException):
    pass


class EnzymeNotFound(InSillyCloFailureException):
    pass


class PlasmidAssemblingFailure(InSillyCloFailureException):
    pass


class InvalideParameterValue(InSillyCloFailureException):
    pass


class TemplateParsingFailure(InSillyCloFailureException):
    pass


class InvalidDelimiterCSV(InSillyCloFailureException):
    pass
