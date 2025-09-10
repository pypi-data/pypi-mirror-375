# __init__.py
# Simon Hulse
# simon.hulse@chem.ox.ac.uk
# Last Edited: Fri 06 Jan 2023 15:43:18 GMT

r"""Module for the creation of text and PDF files of estimation results."""

import os
from pathlib import Path
import platform
import re
import subprocess
from typing import Any, Iterable, List, Optional, Tuple, Union

import numpy as np

from nmrespy import ExpInfo
from nmrespy._colors import GRE, END, USE_COLORAMA
from nmrespy._errors import LaTeXFailedError
from nmrespy._files import (
    check_saveable_path,
    configure_path,
    save_file,
)
from nmrespy._sanity import sanity_check, funcs as sfuncs
from . import textfile, pdffile

if USE_COLORAMA:
    import colorama
    colorama.init()


def check_pdflatex_exe(obj: Any) -> Optional[str]:
    if obj is None:
        obj = "pdflatex"
    elif isinstance(obj, Path):
        obj = str(obj.resolve())
    elif not isinstance(obj, str):
        return "Should be `None`, a str, or a pathlib.Path object."

    which_cmd = "which" if platform.system() in ["Linux", "Darwin"] else "where"
    pdflatex_check = subprocess.run(
        [which_cmd, obj], stdout=subprocess.DEVNULL,
    ).returncode == 0

    if not pdflatex_check:
        return (
            f"\"{obj}\" is not recognised as an executable on your system. "
            "Perhaps you do not have a LaTeX installation on your computer, in "
            "which case you cannot create result files in PDF format."
        )


class ResultWriter(ExpInfo):

    """Class for writing result files. A simple example of using the class is as
    follows:

    .. code:: pycon

        >>> from nmrespy.write import ResultWriter
        >>> writer = ResultWriter(
        ...     expinfo,  # nmrespy.ExpInfo
        ...     params,  # np.ndarray
        ...     errors,  # np.ndarray
        ...     description="Example result file.",  # str
        ... )
        >>> # Write to a text file (defualt if `fmt` isn't given explicitely)
        >>> writer.write(path="result", fmt="txt")
        Saved file /.../result.txt.
        >>> # Write to PDF (suitable LaTeX installation required)
        >>> writer.write(path="result", fmt="pdf")
        Saved file /.../result.pdf.
        You can view and customise the corresponding TeX file at /.../result.tex

    Example outputs:

    * :download:`result.txt <media/write/result.txt>`
    * :download:`result.tex <media/write/result.tex>`
    * :download:`result.pdf <media/write/result.pdf>`
    """
    def __init__(
        self,
        expinfo: ExpInfo,
        params: Iterable[np.ndarray],
        errors: Optional[Iterable[np.ndarray]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Parameters
        ----------
        expinfo
            Experiment information.

        params
            Parameters derived from estimation.

        errors
            Errors derived from estimation. Should be of the same shape as
            ``parameters``.

        description
            A description to be added to the top of result files.
        """
        sanity_check(
            ("expinfo", expinfo, sfuncs.check_expinfo),
            ("description", description, sfuncs.check_str, (), {}, True),
        )

        super().__init__(
            expinfo.dim,
            expinfo.sw(),
            expinfo.offset(),
            expinfo.sfo,
            expinfo.nuclei,
            expinfo.default_pts,
            expinfo.fn_mode,
        )

        # sanity_check(
        #     (
        #         "params", params, sfuncs.check_ndarray_list, (),
        #         {
        #             "dim": 2,
        #             "shapes": len(params) * [(1, 2 * (self.dim + 1))],
        #         },
        #     )
        # )
        # sanity_check(
        #     (
        #         "errors", errors, sfuncs.check_ndarray_list, (),
        #         {
        #             "dim": 2,
        #             "shapes": [
        #                 [(i, s) for i, s in enumerate(p.shape)]
        #                 for p in params
        #             ]
        #         },
        #         True,
        #     )
        # )

        def makeiter(obj):
            return (obj,) if isinstance(obj, np.ndarray) else obj

        self.params = makeiter(params) if params is not None else None
        self.errors = makeiter(errors) if errors is not None else None
        if self.errors is None and self.params is not None:
            self.errors = tuple(len(self.params) * [None])

        self.description = description if description is not None else ""
        self.integrals = tuple([
            self.oscillator_integrals(
                params,
                self.default_pts if self.default_pts is not None else self.dim * [4096],
            )
            for params in self.params
        ]) if self.params is not None else None

    def write(
        self,
        path: Union[str, Path],
        fmt: str = "txt",
        titles: Optional[Iterable[str]] = None,
        experiment_info_sig_figs: Optional[int] = 5,
        parameters_sig_figs: Optional[int] = 5,
        parameters_sci_lims: Optional[Tuple[int, int]] = (-2, 3),
        integral_mode: str = "relative",
        force_overwrite: bool = False,
        fprint: bool = True,
        pdflatex_exe: Optional[Union[str, Path]] = None,
    ) -> None:
        """Write result to text file or PDF.

        Parameters
        ----------
        path
            Path to save the result file to.

        fmt
            Must be one of ``"txt"`` or ``"pdf"``.

        titles
            Titles for each parameter table. If ``None``, give generic titles.

        experiment_info_sig_figs
            The number of significant figures to give to numerical experiment
            inforamtion. If ``None``, the full value will be used.

        parameters_sig_figs
            The number of significant figures to give to parameter values. If
            ``None``, the full value will be used.

        parameters_sci_lims
            Given a value ``(-x, y)``, for ints ``x`` and ``y``, any parameter ``p``
            with a value which satisfies ``p < 10 ** -x`` or ``p >= 10 ** y`` will be
            expressed in scientific notation, rather than explicit notation.
            If ``None``, all values will be expressed explicitely.

        integral_mode
            One of ``"relative"`` or ``"absolute"``. With ``"relative"``, the smallest
            integral will be set to ``1``, and all other integrals will be scaled
            accordingly. With ``"absolute"``, the absolute integral will be computed.
            This should be used if you wish to directly compare different datasets.

        force_overwrite
            If the file specified already exists, and this is set to ``False``, the
            user will br prompted to specify that they are happy overwriting the
            current file.

        fprint
            Specifies whether or not to print information to the terminal.

        pdflatex_exe
            The path to the system's ``pdflatex`` executable.

            .. note::

               You are unlikely to need to set this manually. It is primarily
               present to specify the path to ``pdflatex.exe`` on Windows when
               the NMR-EsPy GUI has been loaded from TopSpin.
        """
        sanity_check(
            ("fmt", fmt, sfuncs.check_one_of, ("txt", "pdf")),
            (
                "titles", titles, sfuncs.check_str_list, (),
                {"length": len(self.params)}, True,
            ),
            (
                "experiment_info_sig_figs", experiment_info_sig_figs,
                sfuncs.check_int, (), {"min_value": 1},
            ),
            (
                "parameters_sig_figs", parameters_sig_figs,
                sfuncs.check_int, (), {"min_value": 1},
            ),
            (
                "parameters_sci_lims", parameters_sci_lims, sfuncs.check_sci_lims,
                (), {}, True,
            ),
            (
                "integral_mode", integral_mode, sfuncs.check_one_of,
                ("relative", "absolute"),
            ),
            ("force_overwrite", force_overwrite, sfuncs.check_bool),
            ("fprint", fprint, sfuncs.check_bool),
        )

        sanity_check(
            ("path", path, check_saveable_path, (fmt, force_overwrite)),
        )

        path = configure_path(path, "txt" if fmt == "txt" else "tex")
        if titles is None:
            titles = tuple(
                [f"Estimation Result{i}" for i in range(1, len(self.params) + 1)]
            )
        titles = (titles,) if isinstance(titles, str) else tuple(titles)

        save_file(
            self._make_file_content(
                fmt,
                titles,
                experiment_info_sig_figs,
                parameters_sig_figs,
                parameters_sci_lims,
                integral_mode,
            ),
            path,
            fprint=fprint,
        )

        if fmt == "pdf":
            sanity_check(
                ("pdflatex_exe", pdflatex_exe, check_pdflatex_exe),
            )
            if pdflatex_exe is None:
                pdflatex_exe = "pdflatex"

            self._compile_tex(path, pdflatex_exe)
            if fprint:
                print(
                    f"{GRE}Saved file {path.with_suffix('.pdf')}.\n"
                    "You can view and customise the corresponding TeX file at "
                    f"{path}.{END}"
                )

    def _construct_experiment_info(
        self,
        sig_figs: int,
    ) -> List[List[str]]:
        """Create Table of experiment information."""
        fstr = lambda x: self._fmtstr(x, sig_figs, None)
        # Titles
        experiment_info = [
            ["Parameter"] + [f"F{i}" for i in range(1, self.dim + 1)]
        ]

        # 1. Nuclei
        if self.nuclei is not None:
            experiment_info.append(
                ["Nucleus"] +
                [x if x is not None else "N/A" for x in self.unicode_nuclei]
            )

        # 2. Transmitter frequency
        if self.sfo is not None:
            experiment_info.append(
                ["Transmitter Frequency (MHz)"] +
                [fstr(x) if x is not None else "N/A"
                 for x in self.sfo]
            )

        # 3. Sweep width (Hz)
        experiment_info.append(
            ["Sweep Width (Hz)"] +
            [fstr(x) for x in self.sw("hz")]
        )

        # 4. Sweep width (ppm)
        if self.sfo is not None:
            experiment_info.append(
                ["Sweep Width (ppm)"] +
                [fstr(x) if sfo is not None else "N/A"
                 for x, sfo in zip(self.sw("ppm"), self.sfo)]
            )

        # 5. Transmitter offset (Hz)
        experiment_info.append(
            ["Transmitter Offset (Hz)"] +
            [fstr(x) for x in self.offset("hz")]
        )

        # 6. Transmitter offset (ppm)
        if self.sfo is not None:
            experiment_info.append(
                ["Transmitter Offset (ppm)"] +
                [fstr(x) if sfo is not None else "N/A"
                 for x, sfo in zip(self.offset("ppm"), self.sfo)]
            )

        return experiment_info

    @property
    def _table_titles(self) -> List[str]:
        titles = ["Osc.", "a", "ϕ (°)"]
        for i in range(self.dim):
            titles.append(
                self._subscript_numbers(f"f{i + 1} (Hz)") if self.dim > 1
                else "f (Hz)"
            )
            if self.sfo is not None and self.sfo[i] is not None:
                titles.append(
                    self._subscript_numbers(f"f{i + 1} (ppm)") if self.dim > 1
                    else "f (ppm)"
                )

        for i in range(self.dim):
            titles.append(
                self._subscript_numbers(f"η{i + 1} (s⁻¹)") if self.dim > 1
                else "η (s⁻¹)"
            )
        titles.append("∫")
        return titles

    def _construct_parameters(
        self,
        sig_figs: int,
        sci_lims: Tuple[int, int],
        integral_mode: str,
    ) -> List[List[str]]:
        """Create Table of parameters."""
        tables = []
        titles = self._table_titles

        fstr = lambda p, e: (
            f"{self._fmtstr(p, sig_figs, sci_lims)} ± "
            f"{self._fmtstr(e, sig_figs, sci_lims)}"
            if e is not None
            else self._fmtstr(p, sig_figs, sci_lims)
        )

        if integral_mode == "relative":
            min_integral = min([np.amin(integrals) for integrals in self.integrals])
        elif integral_mode == "absolute":
            min_integral = 1.0

        integrals = tuple(
            [
                [x / min_integral for x in integs]
                for integs in self.integrals
            ]
        )

        for params, errors, integs in zip(self.params, self.errors, integrals):
            table = [titles]
            if errors is None:
                errors = tuple(len(params) * [None])

            for i, (p, e, integ) in enumerate(
                zip(params, errors, integs),
                start=1,
            ):
                subtable = [str(i)]
                # Amplitude
                subtable.append(fstr(p[0], e[0]))
                # Phase
                subtable.append(
                    fstr(
                        p[1] * 180 / np.pi,
                        e[1] * 180 / np.pi if e[1] is not None else None,
                    )
                )
                # Frequencies
                fslice = slice(2, 2 + self.dim)
                for j, (f, fe) in enumerate(zip(p[fslice], e[fslice])):
                    subtable.append(fstr(f, fe))
                    if self.sfo is not None and self.sfo[j] is not None:
                        subtable.append(
                            fstr(
                                self._convert_value(f, j, "hz->ppm"),
                                self._convert_value(fe, j, "hz->ppm")
                                if fe is not None else None,
                            )
                        )
                # Damping
                dslice = slice(2 + self.dim, None)
                subtable.extend(
                    [fstr(d, de) for d, de in zip(p[dslice], e[dslice])]
                )
                # Integral
                subtable.append(fstr(integ, None))

                table.append(subtable)
            tables.append(table)

        return tables

    def _make_file_content(
        self,
        fmt: str,
        titles: Optional[Iterable[str]],
        experiment_info_sig_figs: int,
        parameters_sig_figs: int,
        parameters_sci_lims: Tuple[int, int],
        integral_mode: str,
    ) -> None:
        if fmt == "txt":
            module = textfile
        elif fmt == "pdf":
            module = pdffile

        experiment_info = self._construct_experiment_info(experiment_info_sig_figs)
        tables = self._construct_parameters(
            parameters_sig_figs,
            parameters_sci_lims,
            integral_mode,
        )

        paramtables = '\n\n'.join(
            [
                module.titled_table(title, table)
                for title, table in zip(titles, tables)
            ]
        )

        return (
            f"{module.header()}\n{self.description}\n\n"
            f"{module.experiment_info(experiment_info)}\n\n"
            f"{paramtables}\n\n"
            f"{module.footer()}"
        )

    @staticmethod
    def _subscript_numbers(text: str) -> str:
        return u''.join(dict(zip(u"0123456789", u"₀₁₂₃₄₅₆₇₈₉")).get(c, c) for c in text)

    @staticmethod
    def _compile_tex(path: Path, pdflatex_exe: Optional[Path]) -> None:
        try:
            subprocess.run(
                [
                    pdflatex_exe,
                    "-halt-on-error",
                    f"-output-directory={path.parent}",
                    path,
                ],
                stdout=subprocess.DEVNULL,
                check=True,
            )
            for suffix in (".out", ".aux", ".log"):
                os.remove(path.with_suffix(suffix))

        except Exception or subprocess.SubprocessError:
            raise LaTeXFailedError(path)

    def _fmtstr(
        self,
        value: float,
        sig_figs: Union[int, None],
        sci_lims: Union[Tuple[int, int], None],
    ) -> str:
        """Convert float to formatted string.

        Parameters
        ----------
        value
            Value to convert.

        sig_figs
            Number of significant figures.

        sci_lims
            Bounds defining thresholds for using scientific notation.
        """
        if isinstance(sig_figs, int):
            value = self._significant_figures(value, sig_figs)

        if (sci_lims is None) or (value == 0):
            return str(value)

        # Determine the value of the exponent to check whether the value should
        # be expressed in scientific or normal notation.
        exp_search = re.search(r"e(\+|-)(\d+)", f"{value:e}")
        exp_sign = exp_search.group(1)
        exp_mag = int(exp_search.group(2))

        if (
            exp_sign == "+" and
            exp_mag < sci_lims[1] or
            exp_sign == "-" and
            exp_mag < -sci_lims[0]
        ):
            return str(value)

        return self._scientific_notation(value)

    @staticmethod
    def _significant_figures(value: float, s: int) -> Union[int, float]:
        """Round a value to a certain number of significant figures.

        Parameters
        ----------
        value
            Value to round.

        s
            Significant figures.

        Returns
        -------
        rounded_value: Union[int, float]
            Value rounded to ``s`` significant figures. If the resulting value
            is an integer, it will be converted from ``float`` to ``int``.
        """
        if value == 0:
            return 0

        value = round(value, s - int(np.floor(np.log10(abs(value)))) - 1)
        # If value of form 123456.0, convert to 123456
        if float(value).is_integer():
            value = int(value)

        return value

    @staticmethod
    def _scientific_notation(value: float) -> str:
        """Convert ``value`` to a string with scientific notation.

        Parameters
        ----------
        value
            Value to process.

        Returns
        -------
        sci_value
            String denoting ``value`` in scientific notation.
        """
        return re.sub(r"\.?0+e(\+|-)0?", r"e\1", f"{value:e}")
