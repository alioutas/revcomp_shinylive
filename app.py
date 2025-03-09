from shiny import App, ui, reactive, render

def reverse_complement(sequence, molecule):
    if molecule == "DNA":
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    elif molecule == "RNA":
        complement = {'A': 'U', 'U': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return ''.join([complement[base] for base in reversed(sequence)])

app_ui = ui.page_fluid(
    ui.tags.style("#MainMenu {visibility: hidden;} footer {visibility: hidden;}"),
    ui.tags.meta(name="google-site-verification", content="4Q0FVMLL8ZaCvpDpmM8qt1W2jvuyEFuoMOqt6p5HlZo"),
    ui.h1("Reverse Complement DNA/RNA Sequence"),
    ui.help_text("designed by Antonios Lioutas"),
    ui.hr(),
    ui.input_text("input_sequence", "Enter your DNA or RNA sequence", value=""),
    ui.output_text_verbatim("output_message"),
    ui.output_ui("output_length"),
    ui.input_radio_buttons("output_type", "Select output nucleic acid type", ["DNA", "RNA"]),
    ui.output_text("reverse_complement_header"),
    ui.output_text_verbatim("reverse_complement_sequence"),
    ui.output_text_verbatim("notification_area"),  # Placeholder for notifications
    ui.tags.button(
        {"type": "button", "class": "btn btn-primary", "id": "copy_button", "onclick": "Shiny.setInputValue('copy_button', Math.random())"},
        "Copy Text"
    ),
    ui.tags.script(
        """
        Shiny.addCustomMessageHandler("copy_to_clipboard", function(message) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(message).then(function() {
                    console.log('Text copied to clipboard');
                    Shiny.setInputValue('copy_success', Math.random());  // Trigger a success event
                }, function(err) {
                    console.error('Failed to copy text: ', err);
                });
            } else {
                console.error('Clipboard API not supported');
            }
        });
        """
    ),
)

def server(input, output, session):
    rev_comp_seq = reactive.Value("")
    notification_message = reactive.Value("")

    @reactive.Calc
    def input_type():
        sequence = input.input_sequence().upper()
        if all(base in 'ATGCN' for base in sequence):
            return "DNA"
        elif all(base in 'AUGC' for base in sequence):
            return "RNA"
        return None

    @output
    @render.text
    @reactive.event(input.input_sequence, ignore_none=False)
    def output_message():
        if input_type() is None:
            return "Invalid input. Please enter a valid DNA or RNA sequence."
        else:
            return ""

    @output
    @render.ui
    @reactive.event(input.input_sequence, ignore_none=False)
    def output_length():
        if input_type() is not None:
            length = len(input.input_sequence())
            if length == 0:
                return ui.div("Input your sequence above.")
            else:
                return ui.div(f"Input sequence is {length} bases long {input_type()}.", style="font-weight: bold;")
        else:
            return ui.div()

    @output
    @render.text
    @reactive.event(input.input_sequence, input.output_type, ignore_none=False)
    def reverse_complement_header():
        sequence = input.input_sequence().upper()
        if sequence:
            molecule_type = input_type()
            if molecule_type is not None:
                return f"Reverse complement {input.output_type()} sequence:"
        return ""

    @output
    @render.text
    @reactive.event(input.input_sequence, input.output_type, ignore_none=False)
    def reverse_complement_sequence():
        sequence = input.input_sequence().upper()
        if sequence:
            molecule_type = input_type()
            if molecule_type is not None:
                if molecule_type != input.output_type():
                    conversion = {'U': 'T'} if input.output_type() == "DNA" else {'T': 'U'}
                    sequence = ''.join([conversion.get(base, base) for base in sequence])
                rev_comp = reverse_complement(sequence, input.output_type())
                rev_comp_seq.set(rev_comp)
                return rev_comp
        rev_comp_seq.set("")
        return ""

    @output
    @render.text
    @reactive.event(notification_message)
    def notification_area():
        return notification_message()

    @reactive.Effect
    @reactive.event(input.copy_button)
    async def copy_to_clipboard():
        await session.send_custom_message("copy_to_clipboard", rev_comp_seq())

    @reactive.Effect
    @reactive.event(input.copy_success)
    def show_notification():
        ui.notification_show(
            f"{rev_comp_seq()} is copied to the clipboard.",
            type="default",
            duration=2,
        )

app = App(app_ui, server)