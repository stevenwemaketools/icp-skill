# Question bank, one slot per turn

Rules that apply to every question: one slot per turn; acknowledge what you already have in one short clause;
give a short example answer so the lead knows the expected shape; accept "no sé" and move on (use the fallback);
never ask the same slot two turns in a row; absorb an answer that fills several slots and skip ahead. Spanish by
default, LatAm neutral, "tú". Mirror English when the lead writes in English. No dash as punctuation.

When the lead pastes a lot at once: map the text onto the slots below first, mark what is filled, and ask only the
missing slots that change the result (ranking, anti-ICP, trigger, market scores). If 80 percent or more is filled,
go straight to Confirm.

## Q0. Route

ES: "¿Qué vendes, a quién se lo vendes hoy y cuántos clientes te han pagado por eso? Un número aproximado basta."
EN: "What do you sell, who buys it today, and how many customers have paid you for it? A rough number is fine."
Fallback: "¿Más o menos de 10 clientes?" decides the path. Fewer than 10, or a new line of business: Path B.

## Path A

**A0. Context** (often answered in Q0): the offer, the ticket band, the geography.
ES: "¿Cuál es tu oferta principal, en qué rango de precio, y en qué ciudad o país vendes?"
EN: "What is your main offer, in what price range, and where do you sell?"

**A1. Roster.** ES: "Nombra tus 5 a 10 mejores clientes, los que clonarías. Pueden ser alias (Marca A, Clínica B).
Y nombra también 2 o 3 de los peores." EN: "Name your 5 to 10 best customers, the ones you would clone. Aliases are
fine. And name 2 or 3 of the worst."
Fallback: "Dime al menos tres buenos y uno malo."

**A2. Ranking.** ES: "De esos buenos, ¿cuáles cumplen más de estas cinco: pagan más, se quedan más tiempo, obtienen
mejores resultados, son fáciles de atender y te refieren a otros? Marca los dos o tres que más cumplen." EN: "Of the
good ones, which satisfy most of these five: pay the most, stay the longest, get the best results, are the easiest to
serve, refer others? Mark the two or three that satisfy most."
Fallback: Claude proposes a ranking from A1 and asks for a yes or a correction.

**A3. Bottom.** ES: "¿Qué tienen en común los peores? Tamaño, cómo llegaron, qué esperaban, cómo pagaban."
EN: "What do the worst ones have in common? Size, how they arrived, what they expected, how they paid."
Fallback: skip; the separation test is then noted as "por confirmar".

**A4. Firmographics of the top.** ES: "Para los mejores: ¿qué tipo de negocio son, de qué tamaño (personas, ventas
o volumen), quién toma la decisión de compra y dónde están?" EN: "For the best ones: what kind of business, what
size (people, sales or volume), who makes the buying decision, and where are they?"

**A5. Before and now.** ES: "¿Cómo estaban esos clientes antes de comprarte y cómo están ahora? Un dato o una frase
por lado." EN: "How were those customers before they bought from you, and how are they now? One fact or one line
each side."
Fallback: skip; `situation_before` and `situation_after` stay empty.

**A6. Aspirations.** ES: "¿Qué querían lograr cuando te compraron, y qué les daba miedo que pasara si no lo
resolvían?" EN: "What were they trying to achieve when they bought, and what were they afraid would happen if they
did not solve it?"

**A7. Buying process 1.** ES: "¿Cuál fue la razón principal por la que te compraron, y qué pasó justo antes (un
cambio, una pérdida, un lanzamiento, un proveedor que falló)?" EN: "What was the main reason they bought, and what
happened right before (a change, a loss, a launch, a vendor that failed)?"

**A8. Buying process 2.** ES: "¿Dónde te vieron por primera vez, qué vieron o leyeron tuyo antes de escribirte, y
alguien los refirió? ¿Cuánto tardaron en comprar desde el primer contacto?" EN: "Where did they first see you, what
did they see or read of yours before writing, did someone refer them? How long from first contact to purchase?"

**A9. Watering holes.** ES: "¿Dónde se juntan esos clientes? Grupos, eventos, podcasts, cuentas que siguen,
software que usan, y quién más les vende." EN: "Where do these customers gather? Groups, events, podcasts, accounts
they follow, software they use, and who else sells to them."

**A10. Reachability.** ES: "¿Podrías listar 100 negocios como esos en una semana? ¿Y hablan entre ellos, se
recomiendan cosas?" EN: "Could you list 100 businesses like those in a week? And do they talk to each other, do they
recommend things to each other?"

**A11. Market indicators.** Propose the four scores from everything so far and ask for corrections.
ES: "Con lo que me contaste, puntúo así de 1 a 10: dolor 8, capacidad de pago 7, fácil de encontrar 8, en
crecimiento 7. ¿Corriges alguno?" EN: "From what you told me I score it like this out of 10: pain 8, purchasing
power 7, easy to target 8, growing 7. Any corrections?"

**A12. Confirm.** Show the North Star sentence, the requirements and the anti-ICP.
ES: "¿Ajustamos algo o generamos el PDF?" EN: "Adjust anything, or generate the PDF?"

## Path B

**B0. What you know.** ES: "Cuéntame qué sabes hacer que la gente ya te paga o te pediría: un dolor que viviste y
resolviste, tu profesión, algo que no dejarías aunque un mes vaya mal, y a quién conoces en ese mundo." EN: "Tell me
what you know how to do that people already pay for or would ask you for: a pain you lived and solved, your
profession, something you would not quit after a bad month, and who you know in that world."

**B1. Candidates.** ES: "Dame 3 a 5 grupos concretos que podrían comprar eso. Si no sabes, te propongo tres."
EN: "Give me 3 to 5 concrete groups that could buy that. If you are not sure, I will propose three."

**B2. Scorecard.** Draft the four indicators per candidate and ask for corrections (see `market-path.md`).
ES: "Puntué cada grupo de 1 a 10 en dolor, capacidad de pago, fácil de encontrar y crecimiento. ¿Qué cambiarías?"
EN: "I scored each group out of 10 on pain, purchasing power, easy to target and growing. What would you change?"

**B3. Pick and hypothesis avatar.** ES: "El grupo con mejor puntaje es X. ¿Lo tomamos? Si sí, dime 3 a 5 cosas
observables que lo definen: tamaño, rol, herramienta, lugar, momento." EN: "The best scoring group is X. Shall we
take it? If yes, give me 3 to 5 observable things that define it: size, role, tool, place, moment."

**B4. Trigger and pain language.** ES: "¿Qué pasa justo antes de que uno de ellos salga a buscar lo que vendes, y
cómo lo dirían con sus palabras?" EN: "What happens right before one of them goes looking for what you sell, and how
would they say it in their own words?"

**B5. Watering holes and reachability.** Same as A9 and A10 in one turn.

**B6. Anti-ICP.** ES: "¿A quién NO le venderías aunque pague? Dame 3 grupos y por qué." EN: "Who would you NOT
sell to even if they pay? Give me 3 groups and why."

**B7. Confirm.** As A12, labelled as a hypothesis.

## "Give me the result now"

Triggers: "dame el resultado ya", "ya", "con eso basta", "give me the result", "just generate it", "skip the rest".
Stop asking. Fill what is missing with explicit assumptions written into `open_questions`, each starting with
"Supuesto:" (or "Assumption:"), require only the render minimum (north_star, 3+ requirements, 3+ anti_icp, 3+
watering holes, 3+ buying path steps, four market scores), and go to Render. Say in one line that the PDF marks the
assumptions under "Por confirmar".
