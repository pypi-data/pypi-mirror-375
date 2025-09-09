/* *****************************************************************************

    trimAl v2.0: a tool for automated alignment trimming in large-scale
                 phylogenetics analyses.

    readAl v2.0: a tool for automated alignment conversion among different
                 formats.

    2009-2019
        Fernandez-Rodriguez V.  (victor.fernandez@bsc.es)
        Capella-Gutierrez S.    (salvador.capella@bsc.es)
        Gabaldon, T.            (tgabaldon@crg.es)

    This file is part of trimAl/readAl.

    trimAl/readAl are free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, the last available version.

    trimAl/readAl are distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with trimAl/readAl. If not, see <http://www.gnu.org/licenses/>.

***************************************************************************** */

#include "FormatHandling/phylip40_state.h"

#include "FormatHandling/FormatManager.h"
#include "defines.h"
#include "utils.h"

namespace FormatHandling {
int phylip40_state::CheckAlignment(std::istream* origin)
{
    origin->seekg(0);
    origin->clear();
    char *firstWord = nullptr, *line = nullptr;
    int blocks = 0;
    std::string buffer;
    
    /* Read first valid line in a safer way */
    do {
        line = utils::readLine(*origin, buffer);
    } while ((line == nullptr) && (!origin->eof()));

    /* If the file end is reached without a valid line, warn about it */
    if (origin->eof())
        return false;

    /* Otherwise, split line */
    firstWord = strtok(line, OTHDELIMITERS);

    /* Phylip Format */
    {
        /* Determine specific phylip format: sequential or interleaved. */

        /* Get number of sequences and residues */
        int sequenNumber = atoi(firstWord);
        int residNumber = 0;
        firstWord = strtok(nullptr, DELIMITERS);
        if(firstWord != nullptr)
            residNumber = atoi(firstWord);
        else {
            return false;
        }

        /* If there is only one sequence, use by default sequential format since
         * it is impossible to determine exactly which phylip format is */
        if((sequenNumber == 1) && (residNumber != 0))
            {
            return true;
        }

            /* If there are more than one sequence, analyze sequences distribution to
             * determine its format. */
        else if((sequenNumber != 0) && (residNumber != 0)) {
            blocks = 0;

            /* Read line in a safer way */
            do {
                line = utils::readLine(*origin, buffer);
            } while ((line == nullptr) && (!origin->eof()));

            /* If the file end is reached without a valid line, warn about it */
            if (origin->eof())
                {
                return false;
            }

            firstWord = strtok(line, DELIMITERS);
            while(firstWord != nullptr) {
                blocks++;
                firstWord = strtok(nullptr, DELIMITERS);
            }

            /* Read line in a safer way */
            do {
                line = utils::readLine(*origin, buffer);
            } while ((line == nullptr) && (!origin->eof()));

            firstWord = strtok(line, DELIMITERS);
            while(firstWord != nullptr) {
                blocks--;
                firstWord = strtok(nullptr, DELIMITERS);
            }
            
            /* If the file end is reached without a valid line, warn about it */
            if (origin->eof())
                return false;

            /* Phylip Interleaved (12) or Sequential (11) */
            return (!blocks) ? 1 : 0;
        }
    }
    return 0;
}

Alignment* phylip40_state::LoadAlignment(std::istream &file)
{
    /* PHYLIP/PHYLIP 4 (Sequential) file format parser */
    Alignment * alig = new Alignment();
    char *str, *line = nullptr;
    int i;
    std::string buffer;

    /* Read first valid line in a safer way */
    do {
        line = utils::readLine(file, buffer);
    } while ((line == nullptr) && (!file.eof()));

    /* If the file end is reached without a valid line, warn about it */
    if (file.eof())
        return nullptr;

    /* Read the input sequences and residues for each sequence numbers */
    str = strtok(line, DELIMITERS);
    alig->numberOfSequences = 0;
    if(str != nullptr)
        alig->numberOfSequences = atoi(str);

    str = strtok(nullptr, DELIMITERS);
    alig->numberOfResidues = 0;
    if(str != nullptr)
        alig->numberOfResidues = atoi(str);

    /* If something is wrong about the sequences or/and residues number,
     * return an error to warn about that */
    if((alig->numberOfSequences == 0) || (alig->numberOfResidues == 0))
        return nullptr;

    /* Allocate memory  for the input data */
    alig->sequences  = new std::string[alig->numberOfSequences];
    alig->seqsName   = new std::string[alig->numberOfSequences];

    /* Read the lines block containing the sequences name + first fragment */
    i = 0;
    while((i < alig->numberOfSequences) && (!file.eof())){

        /* Read lines in a safer way. */
        line = utils::readLine(file, buffer);

        /* It the input line/s are blank lines, skip the loop iteration  */
        if(line == nullptr)
            continue;

        /* First token: Sequence name */
        str = strtok(line, DELIMITERS);
        alig->seqsName[i].append(str, strlen(str));

        /* Trim the rest of the line from blank spaces, tabs, etc and store it */
        str = strtok(nullptr, DELIMITERS);
        while(str != nullptr) {
            alig->sequences[i].append(str, strlen(str));
            str = strtok(nullptr, DELIMITERS);
        }
        i++;
    }

    /* Read the rest of the input file */
    while(!file.eof()) {

        /* Try to get for each sequences its corresponding residues */
        i = 0;
        while((i < alig->numberOfSequences) && (!file.eof())) {
            /* Read lines in a safer way. */
            line = utils::readLine(file, buffer);
            /* It the input line/s are blank lines, skip the loop iteration  */
            if(line == nullptr)
                continue;

            /* Remove from the current line non-printable characters and add fragments
             * to previous stored sequence */
            str = strtok(line, DELIMITERS);
            while(str != nullptr) {
                alig->sequences[i].append(str, strlen(str));
                str = strtok(nullptr, DELIMITERS);
            }
            i++;
        }
    }

    /* Check the matrix's content */
    alig->fillMatrices(true);
    alig->originalNumberOfSequences = alig-> numberOfSequences;
    alig->originalNumberOfResidues = alig->numberOfResidues;
    return alig;
}

bool phylip40_state::SaveAlignment(const Alignment &alignment, std::ostream *output)
{
  
    
   /* Generate output alignment in PHYLIP/PHYLIP 4 format (sequential) */

    int i, j, k = -1, l, maxLongName;
    std::string *tmpMatrix;

    /* Check whether sequences in the alignment are aligned or not.
     * Warn about it if there are not aligned. */
    if (!alignment.isAligned) {
        debug.report(ErrorCode::UnalignedAlignmentToAlignedFormat, new std::string[1] { this->name });
        return false;
    }

    /* Depending on alignment orientation: forward or reverse. Copy directly
     * sequence information or get firstly the reversed sequences and then
     * copy it into local memory */
    if (Machine->reverse)
    {
        /* Allocate local memory for generating output alignment */
        tmpMatrix = new std::string[alignment.originalNumberOfSequences];
        for(i = 0; i < alignment.originalNumberOfSequences; i++)
            tmpMatrix[i] = utils::getReverse(alignment.sequences[i]);
    }
    else tmpMatrix = alignment.sequences;

    /* Depending on if short name flag is activated (limits sequence name up to
     * 10 characters) or not, get maximum sequence name length */
    maxLongName = PHYLIPDISTANCE;
    for(i = 0; (i < alignment.originalNumberOfSequences); i++)
        maxLongName = utils::max(maxLongName, alignment.seqsName[i].size());

    /* Generating output alignment */
    /* First Line: Sequences Number & Residued Number */
    (*output) << " " << alignment.numberOfSequences << " " << alignment.numberOfResidues;

    /* First Block: Sequences Names & First 60 residues */
    for(i = 0; i < alignment.originalNumberOfSequences; i++)
    {
        if (alignment.saveSequences[i] == -1) continue;
        (*output) << "\n" << std::setw(maxLongName + 3) << std::left << alignment.seqsName[i].substr(0, maxLongName);
            
        for (k = 0, l = 0; k < alignment.originalNumberOfResidues && l < 60; k++)
        {
            if (alignment.saveResidues[k] == -1) continue;
            *output << alignment.sequences[i][k];
            l++;
        }
    }

    for (i = k; i < alignment.originalNumberOfResidues; i=k)
    {
        if (alignment.saveResidues[i] == -1) {
            k++;
            continue;
        }
        *output << "\n";
        for (j = 0; j < alignment.originalNumberOfSequences; j++)
        {
            if (alignment.saveSequences[j] == -1) continue;
            *output << "\n";
            for (k = i, l = 0; k < alignment.originalNumberOfResidues && l < 60; k++)
            {
                if (alignment.saveResidues[k] == -1) continue;
                *output << alignment.sequences[j][k];
                l++;
            }
            
        }
    }
    
    *output << "\n\n\n";

    /* Deallocate local memory */
    if (Machine->reverse)
        delete [] tmpMatrix;
    
    return true;
}

bool phylip40_state::RecognizeOutputFormat(const std::string &FormatName)
{
    if (BaseFormatHandler::RecognizeOutputFormat(FormatName)) return true;
    return FormatName == "phylip" || FormatName == "phylip40";
}

}